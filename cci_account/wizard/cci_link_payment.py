# -*- coding: utf-8 -*-
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

form = '''<?xml version="1.0"?>
<form string="Payment links">
    <separator string="Reconcile with already encoded entries" colspan="4"/>
    <newline/>
    <field name="line_ids" colspan="4" nolabel="1" height="300" width="600"/>
</form>'''

fields = {
    'line_ids': {'string': 'Account Moves', 'type': 'many2many', 'relation': 'account.move.line', 'required': False,},
}

def _partial_reconcile(self, cr, uid, data, context):
    form = data['form']
    pool = pooler.get_pool(cr.dbname)
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    list_lines = []
    if len(form['line_ids'][0][2]):
        for line in invoice.move_id.line_id:
            if line.account_id.reconcile:
                list_lines.append(line.id)
        for line in form['line_ids'][0][2]:
            list_lines.append(line)
        if len(list_lines):
            res = pool.get('account.move.line').reconcile_partial(cr, uid, list_lines, 'auto', context=context)
    return {}

def _get_payment(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    if invoice.state in ['draft', 'proforma2', 'cancel']:
        raise wizard.except_wizard(_('Error !'), _('Can not Link payments if invoice is in draft/proforma/cancel'))
    if invoice.type in ['out_invoice', 'in_refund']:
        field = 'credit'
        type = 'receivable'
    else:
        field = 'debit'
        type = 'payable'
    line_ids = pool.get('account.move.line').search(cr, uid, [('partner_id','=',invoice.partner_id.id), ('account_id.type','=',type), (field,'>',0), ('reconcile_id','=',False),('reconcile_partial_id','=',False)])
    fields['line_ids']['domain'] = [('id','in', line_ids)]
    return {
        'line_ids': line_ids
    }

class wizard_link_payment(wizard.interface):
    states = {
        'init': {
            'actions': [_get_payment],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('reconcile','Partial Reconcile')]}
        },
        'reconcile': {
            'actions': [_partial_reconcile],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_link_payment('cci.account.link.payment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
