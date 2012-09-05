# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from mx.DateTime import now
from tools.translate import _

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def _amount_invoiced(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for line in self.browse(cr, uid, ids, context):
            # Calculate invoiced amount with taxes included.
            # Note that if a line is only partially invoiced we consider
            # the invoiced amount 0. 
            # The problem is we can't easily know if the user changed amounts
            # once the invoice was created
            if line.invoiced:
                result[line.id] = line.price_subtotal + self._tax_amount(cr, uid, line)
            else:
                result[line.id] = 0.0
        return result
				
    def _tax_amount(self, cr, uid, line):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c['amount']
        return val

    _columns = {
        'amount_invoiced': fields.function(_amount_invoiced, method=True, string='Invoiced Amount', type='float'),
    }
sale_order_line()

class sale_order(osv.osv):
    _inherit = 'sale.order'

    # Inherited onchange function
    def onchange_partner_id(self, cr, uid, ids, part):
        result = super(sale_order,self).onchange_partner_id(cr, uid, ids, part)
        if part:
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            if partner.available_risk < 0.0:
                result['warning'] = {
                    'title': _('Credit Limit Exceeded'),
                    'message': _('Warning: Credit Limit Exceeded.\n\nThis partner has a credit limit of %(limit).2f and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.total_debt,
                    }
                }
        return result

    def _amount_invoiced(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for order in self.browse(cr, uid, ids, context):
            if order.invoiced:
                amount = order.amount_total
            else:
                amount = 0.0
                for line in order.order_line:
                    amount += line.amount_invoiced
            result[order.id] = amount
        return result

    _columns = {
        'amount_invoiced': fields.function(_amount_invoiced, method=True, string='Invoiced Amount', type='float'),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('wait_risk', 'Waiting Risk Approval'),
            ], 'Order State', readonly=True, help=_("Gives the state of the quotation or sale order. The exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the packing list process (Shipping Exception). The 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the date 'Date Ordered'."), select=True),
    }
sale_order()


class partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _unpayed_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append( partner.property_account_receivable.id )
            if partner.property_account_payable:
                accounts.append( partner.property_account_payable.id )
            line_ids = self.pool.get('account.move.line').search( cr, uid, [
                ('partner_id','=',partner.id), 
                ('account_id', 'in', accounts), 
                ('reconcile_id','=',False), 
                ('date_maturity','<',today),
            ], context=context) 
            # Those that have amount_to_pay == 0, will mean that they're circulating. The payment request has been sent
            # to the bank but have not yet been reconciled (or the date_maturity has not been reached).
            amount = 0.0
            for line in self.pool.get('account.move.line').browse( cr, uid, line_ids, context ):
                #amount += -line.amount_to_pay
                amount += line.debit - line.credit
            res[partner.id] = amount
        return res

    def _circulating_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append( partner.property_account_receivable.id )
            if partner.property_account_payable:
                accounts.append( partner.property_account_payable.id )
            line_ids = self.pool.get('account.move.line').search( cr, uid, [
                ('partner_id','=',partner.id), 
                ('account_id', 'in', accounts), 
                ('reconcile_id','=',False), 
                '|', ('date_maturity','>=',today), ('date_maturity','=',False)
            ], context=context) 
            # Those that have amount_to_pay == 0, will mean that they're circulating. The payment request has been sent
            # to the bank but have not yet been reconciled (or the date_maturity has not been reached).
            amount = 0.0
            for line in self.pool.get('account.move.line').browse( cr, uid, line_ids, context ):
                #amount += line.debit - line.credit
                amount += line.debit - line.credit + line.amount_to_pay
            res[partner.id] = amount
        return res

    def _pending_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append( partner.property_account_receivable.id )
            if partner.property_account_payable:
                accounts.append( partner.property_account_payable.id )
            line_ids = self.pool.get('account.move.line').search( cr, uid, [
                ('partner_id','=',partner.id), 
                ('account_id', 'in', accounts), 
                ('reconcile_id','=',False), 
                '|', ('date_maturity','>=',today), ('date_maturity','=',False)
            ], context=context) 
            # Those that have amount_to_pay == 0, will mean that they're circulating. The payment request has been sent
            # to the bank but have not yet been reconciled (or the date_maturity has not been reached).
            amount = 0.0
            for line in self.pool.get('account.move.line').browse( cr, uid, line_ids, context ):
                #amount += line.debit - line.credit
                amount += -line.amount_to_pay
            res[partner.id] = amount
        return res

    def _draft_invoices_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        for id in ids:
            invids = self.pool.get('account.invoice').search( cr, uid, [
                ('partner_id','=',id), 
                ('state','=','draft'), 
                '|', ('date_due','>=',today), ('date_due','=',False)
            ], context=context )
            val = 0.0
            for invoice in self.pool.get('account.invoice').browse( cr, uid, invids, context ):
                # Note that even if the invoice is in 'draft' state it can have an account.move because it 
                # may have been validated and brought back to draft. Here we'll only consider invoices with 
                # NO account.move as those will be added in other fields.
                if invoice.move_id:
                    continue
                if invoice.type in ('out_invoice','in_refund'):
                    val += invoice.amount_total
                else:
                    val -= invoice.amount_total
            res[id] = val
        return res

    def _pending_orders_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            sids = self.pool.get('sale.order').search( cr, uid, [
                ('partner_id','=',id),
                ('state','not in',['draft','cancel','wait_risk'])
            ], context=context )
            total = 0.0
            for order in self.pool.get('sale.order').browse(cr, uid, sids, context):
                total += order.amount_total - order.amount_invoiced
            res[id] = total
        return res

    def _total_debt(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse( cr, uid, ids, context ):
            pending_orders = partner.pending_orders_amount or 0.0
            circulating = partner.circulating_amount or 0.0
            unpayed = partner.unpayed_amount or 0.0
            pending = partner.pending_amount or 0.0
            draft_invoices = partner.draft_invoices_amount or 0.0
            res[partner.id] = pending_orders + circulating + unpayed + pending + draft_invoices
        return res

    def _available_risk(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse( cr, uid, ids, context ):
            res[partner.id] = partner.credit_limit - partner.total_debt
        return res

    def _total_risk_percent(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse( cr, uid, ids, context ):
            if partner.credit_limit:
                res[partner.id] = 100.0 * partner.total_debt / partner.credit_limit
            else:
                res[partner.id] = 100
        return res

    _columns = {
        'unpayed_amount': fields.function(_unpayed_amount, method=True, string=_('Expired Unpaid Payments'), type='float'),
        'pending_amount': fields.function(_pending_amount, method=True, string=_('Unexpired Pending Payments'), type='float'),
        'draft_invoices_amount': fields.function(_draft_invoices_amount, method=True, string=_('Draft Invoices'), type='float'),
        'circulating_amount': fields.function(_circulating_amount, method=True, string=_('Payments Sent to Bank'), type='float'),
        'pending_orders_amount': fields.function(_pending_orders_amount, method=True, string=_('Uninvoiced Orders'), type='float'),
        'total_debt': fields.function(_total_debt, method=True, string=_('Total Debt'), type='float'),
        'available_risk': fields.function(_available_risk, method=True, string=_('Available Credit'), type='float'),
        'total_risk_percent': fields.function(_total_risk_percent, method=True, string=_('Credit Usage (%)'), type='float')
    }
partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
