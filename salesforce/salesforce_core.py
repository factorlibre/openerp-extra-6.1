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
import salesforce_osv
#If debug is true everything is logged
DEBUG = True
TIMEOUT = 2

#class res_partner(osv.osv):
#    _inherit="res.partner"
#    _columns = {
#        'salesforce_id':fields.char('Salesforce Reference',size=100),
#        'salesforce_partner':fields.boolean('Sales Force Partner?',readonly=True,store=True)
#                }
#res_partner()

class res_partner(salesforce_osv.salesforce_osv):
    _name="res.partner"
    _inherit="res.partner"
    _columns = {
        'salesforce_id':fields.char('Salesforce Reference',size=100),
        'salesforce_partner':fields.boolean('Sales Force Partner?',readonly=True,store=True)
        }
res_partner()

#class res_partner_contact(osv.osv):
#    _inherit = "res.partner.contact"
#    _columns = {
#        'salesforce_id':fields.char('Salesforce Reference',size=100)
#                }
#res_partner_contact()

class res_partner_contact(salesforce_osv.salesforce_osv):
    _name="res.partner.contact"
    _inherit = "res.partner.contact"
    _columns = {
        'salesforce_id':fields.char('Salesforce Reference',size=100)
                }   
res_partner_contact()

class salesforce_inttools(osv.osv_memory):
    _name="salesforce.inttools"
    _description = "Tools to operate the tool"
    _columns = {
        'referential':fields.many2one('external.referential','Select Account',required=True)
                }
    def import_partners(self,cr,uid,ids,context={}):
        if ids:
            ref_id = self.read(cr,uid,ids,[])
            if ref_id:
                referential = self.pool.get('external.referential').browse(cr,uid,ref_id[0]['id'])
                conn = self.pool.get('salesforce_osv').external_connection(cr,uid,referential)
                self.pool.get('res.partner').sync_import(cr,uid,conn,ids[0],defaults={'salesforce_partner':True}, context={})
    
    def import_partner_contacts(self,cr,uid,ids,context={}):
        if ids:
            ref_id = self.read(cr,uid,ids,[])
            if ref_id:
                referential = self.pool.get('external.referential').browse(cr,uid,ref_id[0]['id'])
                conn = self.pool.get('salesforce_osv').external_connection(cr,uid,referential)
                self.pool.get('res.partner.contact').sync_import(cr,uid,conn,ids[0],defaults={}, context={})

salesforce_inttools()

class external_referential(salesforce_osv.salesforce_osv):
    _inherit = "external.referential"
    _columns = {
        'timestamp_last':fields.char('Last time stamp',size=100)
                }
    
            
external_referential()