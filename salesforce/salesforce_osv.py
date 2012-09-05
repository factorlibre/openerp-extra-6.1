##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Sharoon Thomas.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
from osv import osv,fields
from tools.translate import _
import netsvc
#Check if pyax exists and import it
try:
    from pyax.connection import Connection
except:
    raise osv.except_osv(_('Error!'), _('The pyax module is not installed\nRefer to documentation.'))
try:
    from base_external_referentials import external_osv
except:
    raise osv.except_osv(_('Error!'), _('Base External Referentials Module is not installed\nRefer to documentation.'))
#If debug is true everything is logged
DEBUG = True
TIMEOUT = 2
class Connection_wrapper(object):
    def __init__(self, username='', password='', debug=False):
        self.username = username
        self.password = password
        self.debug = debug
        self.result = {}
        self.logger = netsvc.Logger()
        try:
            self.sfdc = Connection.connect(self.username,self.password)
        except:
            self.sfdc = False
    
    def connect_check(self):
        try:
            timestamp = self.sfdc.getServerTimestamp()
            self.logger.notifyChannel('SalesForce', netsvc.LOG_INFO, 'Connected to server successfully. Server Timestamp : %s' % (timestamp,))
            return True
        except:
            try:
                self.sfdc = Connection.connect(self.username,self.password)
            except:
                self.logger.notifyChannel('SalesForce', netsvc.LOG_WARNING, 'Could not connect to the server')
                return False
            return True

    def call(self,query_text,arguments):
        result=False
        qry =  query_text
        if arguments:
            qry += " where "
        for each_tuple in arguments:
            qry += each_tuple[0] + " " + each_tuple[1] + " " + each_tuple[2] 
        if DEBUG:
            self.logger.notifyChannel('SalesForce', netsvc.LOG_INFO, 'New Query Generated : %s' % (qry,))
        if self.connect_check():
            result = self.sfdc.query(qry)
            if DEBUG:
                self.logger.notifyChannel('SalesForce', netsvc.LOG_INFO, 'Data for Query fetched : %s' % (result,))
        print type(result)
        return result
Connection_wrapper()

class salesforce_osv(external_osv.external_osv):
    _name = "salesforce_osv"
    def external_connection(self, cr, uid,referential):
        conn_wrap = Connection_wrapper(referential.apiusername, referential.apipass)
        return conn_wrap or False
    
    def sync_import(self,cr,uid,conn,external_referential_id,defaults={}, context={}):
        if not 'ids_or_filter' in context.keys():
            context['ids_or_filter'] = []
        result = {'create_ids': [], 'write_ids': []}
        mapping_id = self.pool.get('external.mapping').search(cr,uid,[('model','=',self._name),('referential_id','=',external_referential_id)])
        if mapping_id:
            data = []
            list_method = self.pool.get('external.mapping').read(cr,uid,mapping_id[0],['external_list_method']).get('external_list_method',False)
            if list_method:
                data = conn.call(list_method, context['ids_or_filter'])
                #it may happen that list method doesn't provide enough information, forcing us to use get_method on each record (case for sale orders)
                if context.get('one_by_one', False):
                    for record in data:
                        id = record[self.pool.get('external.mapping').read(cr, uid, mapping_id[0],['external_key_name'])['external_key_name']]
                        get_method = self.pool.get('external.mapping').read(cr,uid,mapping_id[0],['external_get_method']).get('external_get_method',False)
                        rec_data = [conn.call(get_method, [id])]
                        rec_result = self.ext_import(cr, uid, rec_data, external_referential_id, defaults, context)
                        result['create_ids'].append(rec_result['create_ids'])
                        result['write_ids'].append(rec_result['write_ids'])
                else:
                    result = self.ext_import(cr, uid, data, external_referential_id, defaults, context)
        return result or False

salesforce_osv()