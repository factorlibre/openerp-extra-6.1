# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import wizard
import pooler

perform_form = '''<?xml version="1.0"?>
    <form string="Performance monitor">
        <field name="name" />
        <field name="date"/>
    </form>'''
    
def _get_methods(self, cr, uid, context):
    cr.execute("select distinct(name) from dm_perf_monitor")
    return map(lambda x: (x[0],x[0]), cr.fetchall())
    
def _performance(self, cr, uid, data, context):
    perform_obj = pooler.get_pool(cr.dbname).get('dm.perf_monitor')
    view_res = pooler.get_pool(cr.dbname).get('ir.ui.view').search(cr, uid, [('name', '=', 'dm.perf_monitor.graph')])
    name = data['form']['name']
    wiz_date = data['form']['date']
    cr.execute("select id from dm_perf_monitor where name = %s and date >= %s and date <= %s", (name, (wiz_date + ' 00:00:00'), (wiz_date + ' 23:59:59')))
    performance_ids = map(lambda x: x[0], cr.fetchall())
    value = {
        'domain': [('id', 'in', performance_ids)],
        'name': 'Performances',
        'view_type': 'form',
        'view_mode': 'graph,tree,form',
        'res_model': 'dm.perf_monitor',
        'view_id': view_res,
        'context': {},
        'type': 'ir.actions.act_window'
        }         
    return value
    
perform_fields = { # {{{
    'name': {
                'string': 'Method', 
                'type': 'selection',
                'selection': _get_methods,
                'required': True
                },
    'date': {
                'string': 'Date',
                'type': 'date',
                'required': True
             },
    } # }}}

class wizard_performance_monitor(wizard.interface):
    
    states = {
        'init': {
            'actions': [],
            'result': {
                       'type': 'form', 
                       'arch': perform_form, 
                       'fields': perform_fields, 
                       'state': [('end', 'Cancel'), ('done', 'Performance')]
                    }
                },
        'done': {
            'actions': [],
            'result': {
                        'type': 'action',
                        'action': _performance,
                        'state': 'end'
                    }
                },
            }

wizard_performance_monitor("wizard.performance.monitor")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
