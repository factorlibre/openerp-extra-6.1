# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008-2009 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import netsvc
import pooler
import xmlrpclib

arch = '''<?xml version="1.0"?>
<form string="Model fields on New and Old servers">
    <group colspan="2" col="4">
        <separator string="Model fields on New server"/>
        <newline/>
        <field name="new_model" nolabel="1" height="550" width="450"/>
    </group>
    <group colspan="2" col="2">
        <separator string="Model fields on Old server"/>
        <newline/>
        <field name="old_model" nolabel="1" height="550" width="450"/>
    </group>
</form>'''

fields = {
    'new_model': {'type': 'text', 'string': 'Model fields on New server', 'readonly': False},
    'old_model': {'type': 'text', 'string': 'Model fields on Old server', 'readonly': False},
}

def _compare_models(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    field_on_new_str=field_on_old_str=''
    ############# Get Connection ############
    id = pool.get('migration.server.connect_config').search(cr, uid, [], limit=1)
    remote_config = pool.get('migration.server.connect_config').read(cr, uid, id)[0]
    sock_common = xmlrpclib.ServerProxy ('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/common', encoding="UTF-8")
    remote_uid = sock_common.login(remote_config['db_name'], remote_config['name'], remote_config['password'])
    sock = xmlrpclib.ServerProxy('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/object', encoding="UTF-8")
    #########################################
    for id in data['ids']:
        import_model_name = pool.get("migration.import_models").browse(cr, uid, id, {}).name.model
        ############# Old Server #############
        old_field_ids = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.model.fields', 'search', [('model','=', import_model_name)])
        if old_field_ids:
            field_on_old = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.model.fields', 'read', old_field_ids, ['name','field_description','ttype'])
            field_on_old_list = map(lambda field: field['name']+' ['+field['field_description']+'], Type: '+field['ttype']+'\n', field_on_old)
            field_on_old_list.sort()
        ############# Local Server #############
        new_field_ids = pool.get("ir.model.fields").search(cr, uid, [('model','=', import_model_name)])
        field_on_new = pool.get('ir.model.fields').read(cr, uid,  new_field_ids, ['name','field_description','ttype'])
        ########################################
        field_on_new_list = map(lambda field: field['name']+' ['+field['field_description']+'], Type: '+field['ttype']+'\n', field_on_new)
        field_on_new_list.sort()
        #field_on_old_list = map(lambda field: field['name']+' ['+field['field_description']+'], Type: '+field['ttype']+'\n', field_on_old)
        #field_on_old_list.sort()
        field_on_new_str += "<<<<<<<<<< Model: "+import_model_name+" >>>>>>>>>>\n"+reduce(lambda x, y: x+y, field_on_new_list)
        if old_field_ids:
            field_on_old_str += "<<<<<<<<<< Model: "+import_model_name+" >>>>>>>>>>\n"+reduce(lambda x, y: x+y, field_on_old_list)
        else:
            field_on_old_str += "Warning! On the old server object model '"+import_model_name+"' is not exist.\n"
    return {'new_model': field_on_new_str, 'old_model': field_on_old_str}

class compare_models_wizard(wizard.interface):
    states = {
        'init': {
                    'actions': [_compare_models],
                    'result': {'type': 'form', 'arch': arch, 'fields': fields,'state': [('end', 'Close')]}
         }
    }

compare_models_wizard('migration.import_models.menu')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

