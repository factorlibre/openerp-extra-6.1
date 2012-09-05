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

from tools.translate import _

camp_doc_form = '''<?xml version="1.0"?>
    <form string="Resend Campaign Documents">
        <field name="state"/>
    </form>'''
    
camp_doc_fields = { # {{{
    'state': {
              'string': 'Resend all documents in ', 
              'type': 'selection',
              'selection': [('selection','Selection'),('error', 'Error State'),
                ('done', 'Done State'), ('resent', 'Resent State')],
              'default': lambda *a: 'selection'
             },
    } # }}}

def _resend_document(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    camp_doc_obj = pool.get('dm.campaign.document')
    wi_obj = pool.get('dm.workitem')
    if data['form']['state']:
        if data['form']['state'] == 'selection':
            camp_doc_obj.state_resent(cr, uid, data['ids'], context)
        else:
            camp_doc_ids = camp_doc_obj.search(cr, uid, [('state', '=', data['form']['state'])])
            camp_doc_obj.state_resent(cr, uid, camp_doc_ids, context)
    return {}

class wizard_resend_campaign_document(wizard.interface):
    
    states = {
        'init': {
            'actions': [],
            'result': {
                       'type': 'form', 
                       'arch': camp_doc_form, 
                       'fields': camp_doc_fields, 
                       'state': [('end', 'Cancel'), ('done', 'Resend')]
                       }
                },
        'done': {
            'actions': [],
            'result': {
                       'type': 'action',
                       'action': _resend_document,
                       'state': 'end'
                    }
                },
            }

wizard_resend_campaign_document("wizard.resend.campaign.documents")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
