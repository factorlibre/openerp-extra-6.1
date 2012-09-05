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
import time

from tools.translate import _

seg_form = '''<?xml version="1.0"?>
    <form string="Process Customers file">
        <field name="action_date" />
        <field name="step_id" domain="[('type_id.flow_start','=',True)]"/>
    </form>'''
    
seg_fields = { # {{{
    'action_date': {
                    'string': 'Action Date', 
                    'type': 'datetime',
                    'default': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                },
    'step_id': {
                'string': 'Offer Step',
                'type': 'many2one',
                'relation': 'dm.offer.step',
             },
    } # }}}

def _process_customer(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    workitem_obj = pool.get('dm.workitem')
    segment_obj = pool.get('dm.campaign.proposition.segment')
    segment_ids = segment_obj.browse(cr, uid, data['ids'])
    for seg_id in segment_ids:
        if seg_id.customers_file_id:
            for address_id in seg_id.customers_file_id.address_ids:
                workitem_obj.create(cr, uid, {
                                    'address_id': address_id.id,
                                    'action_time': data['form']['action_date'],
                                    'step_id': data['form']['step_id'],
                                    'is_realtime': False
                                    })
        else:
            raise wizard.except_wizard(_('Error'),_('There is no customer file for this segment'))
    return {}

class wizard_process_customers_file(wizard.interface):
    
    states = {
        'init': {
            'actions': [],
            'result': {
                       'type': 'form', 
                       'arch': seg_form, 
                       'fields': seg_fields, 
                       'state': [('end', 'Cancel'), ('done', 'Process')]
                    }
                },
        'done': {
            'actions': [],
            'result': {
                        'type': 'action',
                        'action': _process_customer,
                        'state': 'end'
                    }
                },
            }

wizard_process_customers_file("wizard.process.customer.file")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
