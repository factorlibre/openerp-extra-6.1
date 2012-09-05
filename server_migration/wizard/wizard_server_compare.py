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
<form string="Compare New and Old server's modules">
    <label string="This function will compare installed modules on new and old servers:" colspan="4" align="0.0"/>
</form>'''
fields = { }

arch_module = '''<?xml version="1.0"?>
<form string="Not installed modules">
    <group colspan="2" col="4">
        <separator string="Not installed modules on New server"/>
        <newline/>
        <field name="local_modules" nolabel="1" height="550" width="450"/>
    </group>
    <group colspan="2" col="2">
        <separator string="Not installed modules on Old server"/>
        <newline/>
        <field name="remote_modules" nolabel="1" height="550" width="450"/>
    </group>
</form>'''

fields_module = {
    'local_modules': {'type': 'text', 'string': 'Not installed modules on New server', 'readonly': False},
    'remote_modules': {'type': 'text', 'string': 'Not installed modules on Old server', 'readonly': False},
}

def _compare_servers(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    ############# Old Server #############
    ############# Get Connection ############
    id = pool.get('migration.server.connect_config').search(cr, uid, [], limit=1)
    remote_config = pool.get('migration.server.connect_config').read(cr, uid, id)[0]
    sock_common = xmlrpclib.ServerProxy ('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/common', encoding="UTF-8")
    remote_uid = sock_common.login(remote_config['db_name'], remote_config['name'], remote_config['password'])
    sock = xmlrpclib.ServerProxy('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/object', encoding="UTF-8")
    #########################################
    remote_installed_modules_ids = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.module.module', 'search', [('state','=','installed')])
    remote_installed_modules = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.module.module', 'read', remote_installed_modules_ids, ['name','shortdesc'])
    remote_modules_ids = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.module.module', 'search', [])
    remote_modules = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.module.module', 'read', remote_modules_ids, ['name','shortdesc'])
    ############# Local Server #############
    local_installed_modules_ids = pool.get('ir.module.module').search(cr, uid, [('state','=','installed')])
    local_installed_modules = pool.get('ir.module.module').read(cr, uid, local_installed_modules_ids, ['name','shortdesc'])
    local_modules_ids = pool.get('ir.module.module').search(cr, uid, [])
    local_modules = pool.get('ir.module.module').read(cr, uid, local_modules_ids, ['name','shortdesc'])
    ########################################

    not_installed_onlocal = ''
    not_installed_onremote = ''
    local_installed_modules_names = map(lambda x: x['name'], local_installed_modules)
    remote_installed_modules_names = map(lambda x: x['name'], remote_installed_modules)
    local_modules_names = map(lambda x: x['name'], local_modules)
    remote_modules_names = map(lambda x: x['name'], remote_modules)

    for module in remote_installed_modules:
        if module['name'] not in local_installed_modules_names:
            not_installed_onlocal += module['name']+' ['+module['shortdesc']+']'
            if module['name'] not in local_modules_names:
                not_installed_onlocal += ' - NOT FOUND IN SYSTEM\n'
            else:
                not_installed_onlocal += ' - NOT IS INSTALLED\n'
    for module in local_installed_modules:
        if module['name'] not in remote_installed_modules_names:
            not_installed_onremote += module['name']+' ['+module['shortdesc']+']'
            if module['name'] not in remote_modules_names:
                not_installed_onremote += ' - NOT FOUND IN SYSTEM\n'
            else:
                not_installed_onremote += ' - NOT IS INSTALLED\n'

    return {'local_modules': not_installed_onlocal, 'remote_modules': not_installed_onremote}

class compare_servers_wizard(wizard.interface):
    states = {
        'init': {
                    'actions': [],
                    'result': {'type': 'form', 'arch': arch, 'fields': fields,'state': [('end', 'Cancel', 'gtk-cancel'),('compare', 'Compare Servers', 'gtk-ok', True)]}
         },
        'compare': {
            'actions': [_compare_servers],
            'result': {'type': 'form', 'arch': arch_module, 'fields': fields_module,'state': [('end', 'Close')]}
        }
    }

compare_servers_wizard('migration.server_compare.menu')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

