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
import netsvc
import pooler
import time
from tools.translate import _
import tools

pay_form = '''<?xml version="1.0"?>
<form string="Pay invoice">
    <field name="amount"/>
    <newline/>
    <field name="name"/>
    <field name="date"/>
    <field name="journal_id"/>
    <field name="period_id"/>
    <!-- <separator string="Reconcile with already encoded entries" colspan="4"/>
    <newline/>
    <field name="line_ids" colspan="4" nolabel="1" height="300" /> -->
</form>'''

pay_fields = {
    'amount': {'string': 'Amount paid', 'type':'float', 'required':True, 'digits': (16,int(tools.config['price_accuracy']))},
    'name': {'string': 'Entry Name', 'type':'char', 'size': 64, 'required':True},
    'date': {'string': 'Payment date', 'type':'date', 'required':True, 'default':lambda *args: time.strftime('%Y-%m-%d')},
    'journal_id': {'string': 'Journal/Payment Mode', 'type': 'many2one', 'relation':'account.journal', 'required':True, 'domain':[('type','=','cash')]},
    'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period', 'required':True},
    #'line_ids': {'string': 'Account Moves', 'type': 'many2many', 'relation': 'account.move.line', 'required': False,},
}

def _pay_and_reconcile(self, cr, uid, data, context):
    form = data['form']
    period_id = form.get('period_id', False)
    journal_id = form.get('journal_id', False)
    writeoff_account_id = form.get('writeoff_acc_id', False)
    writeoff_journal_id = form.get('writeoff_journal_id', False)
    pool = pooler.get_pool(cr.dbname)
    cur_obj = pool.get('res.currency')
    amount = form['amount']
    context['analytic_id'] = form.get('analytic_id', False)

    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
    journal = pool.get('account.journal').browse(cr, uid, data['form']['journal_id'], context)
    # Compute the amount in company's currency, with the journal currency (which is equal to payment currency)
    # when it is needed :  If payment currency (according to selected journal.currency) is <> from company currency
    if journal.currency and invoice.company_id.currency_id.id<>journal.currency.id:
        ctx = {'date':data['form']['date']}
        amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)
        currency_id = journal.currency.id
        # Put the paid amount in currency, and the currency, in the context if currency is different from company's currency
        context.update({'amount_currency':form['amount'],'currency_id':currency_id})

    # Take the choosen date
    if form.has_key('comment'):
        context.update({'date_p':form['date'],'comment':form['comment']})
    else:
        context.update({'date_p':form['date'],'comment':False})

    acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
    if not acc_id:
        raise wizard.except_wizard(_('Error !'), _('Your journal must have a default credit and debit account.'))

#    list_lines = []
#    if len(form['line_ids'][0][2]):
#        for line in invoice.move_id.line_id:
#            if line.account_id.reconcile:
#                list_lines.append(line.id)
#        for line in form['line_ids'][0][2]:
#            list_lines.append(line)
#        if len(list_lines):
#            res = pool.get('account.move.line').reconcile_partial(cr, uid, list_lines, 'auto', context=context)

    pool.get('account.invoice').pay_and_reconcile(cr, uid, [data['id']],
            amount, acc_id, period_id, journal_id, writeoff_account_id,
            period_id, writeoff_journal_id, context, data['form']['name'])

    return {}

def _get_period(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    ids = pool.get('account.period').find(cr, uid, context=context)
    period_id = False
    if len(ids):
        period_id = ids[0]
    invoice = pool.get('account.invoice').browse(cr, uid, data['id'], context)
#    if invoice.type in ['out_invoice', 'in_refund']:
#        field = 'credit'
#        type = 'receivable'
#    else:
#        field = 'debit'
#        type = 'payable'
#    line_ids = pool.get('account.move.line').search(cr, uid, [('partner_id','=',invoice.partner_id.id), ('account_id.type','=',type), (field,'>',0), ('reconcile_id','=',False),('reconcile_partial_id','=',False)])
#    pay_fields['line_ids']['domain'] = ('id','in', line_ids),
    if invoice.state in ['draft', 'proforma2', 'cancel']:
        raise wizard.except_wizard(_('Error !'), _('Can not pay draft/proforma/cancel invoice.'))
    return {
        'period_id': period_id,
        'amount': invoice.residual,
        'date': time.strftime('%Y-%m-%d'),
#        'line_ids': line_ids
    }

class wizard_pay_invoice(wizard.interface):
    states = {
        'init': {
            'actions': [_get_period],
            'result': {'type':'form', 'arch':pay_form, 'fields':pay_fields, 'state':[('end','Cancel'),('reconcile','Payment')]}
        },
        'reconcile': {
            'actions': [_pay_and_reconcile],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_pay_invoice('cci.account.invoice.pay')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
