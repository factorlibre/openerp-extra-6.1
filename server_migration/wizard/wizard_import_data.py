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
from osv import fields
import time
from mx import DateTime
from mx.DateTime import now

arch = '''<?xml version="1.0"?>
<form string="Import data from Old to New server">
    <label string="This function will import data for selected object models from old to new server:" colspan="4" align="0.0"/>
</form>'''
form_fields = { }

_result_form = '''<?xml version="1.0"?>
<form string="Report of data import results">
    <separator string="Report text" colspan="4"/>
    <field name="res_text" nolabel="1" width="550" height="300"/>
</form>'''

_result_window_fields = {
    'res_text': {'type': 'text', 'string': 'Data Import Report'},
}

class import_data_config_wizard(wizard.interface):
    '''
        Server migration configuration wizard class
    '''
    form = '''<?xml version="1.0"?>
    <form string="Create Migration Scheduler">
        <field name="import_model_ids" height="200" colspan="4" nolabel="1"/>
		<field name="print_log" colspan="4"/>
    </form>'''

    fields = {
        'import_model_ids': {'string':'Import Models','type': 'many2many','relation': 'migration.import_models'},
        'print_log': {'string':'Print Log to Console','type': 'boolean'}
    }

    def _do_process(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)

        res = {}
        res['name'] = 'Scheduled Migration, '+time.strftime('%Y-%m-%d %H:%M:%S')
        res['nextcall'] = (now()+DateTime.RelativeDateTime(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        res['priority'] = 5
        res['numbercall'] = 1
        res['interval_type'] = 'minutes'
        res['interval_number'] = 1
        res['model'] = 'migration.schedule'
        #res['args'] = data['form'][0][2]
        res['function'] = '_import_data'
        
        action_ids = []
        name_list = []
        for act in pool.get("migration.import_models").read(cr, uid, data['form']['import_model_ids'][0][2], ['name','actions']):
            name_list.append(act['name'][1])
            action_ids += act['actions']
        name = ', '.join(name_list)
        if len(name)>64:
            name = name[:61]+'...'

        cron_id = pool.get('ir.cron').create(cr, uid, res)
        id = pool.get('migration.schedule').create(cr, uid, {'name':name,'import_model_ids':data['form']['import_model_ids'],'actions_ids':[(6,0,action_ids)],
                        'cron_id':cron_id,'print_log':data['form']['print_log']})
        pool.get('ir.cron').write(cr, uid, cron_id, {'args':[id,data['form']['import_model_ids'][0][2]]})
        return {
			'domain': "[('id','=', "+str(id)+")]",
			'name': 'Scheduled Migrations',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'migration.schedule',
			'view_id': False,
			'type': 'ir.actions.act_window'
        }
    
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', 'Cancel', 'gtk-cancel'), ('start', 'Start', 'gtk-ok', True))},
        },
        'start': {
            'actions': [],
            'result' : {'type':'action', 'action':_do_process, 'state':'end'},
        },
    }
import_data_config_wizard('migration.import_data_config_wizard')


