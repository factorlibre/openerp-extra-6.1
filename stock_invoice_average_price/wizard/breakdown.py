# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import osv, fields
import decimal_precision as dp


class invoice_cost_breakdown(osv.osv_memory):
    """
    This wizard breaks down the cost of the selected transport and custom
    invoices to purchase invoices.
    """

    _name = "invoice.cost.breakdown"
    _description = "Breaks down cost invoices"

    def default_get(self, cr, uid, fields, context=None):
        data = self._default_get(cr, uid, fields, context=context)
        for f in data.keys():
            if f not in fields:
                del data[f]
        return data

    def _default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        data = super(invoice_cost_breakdown, self).default_get(cr, uid,
                                                    fields, context=context)
        data['state'] = 'step1'
        if context['active_model'] == 'account.invoice':
            amount = 0.0
            for invoice in invoice_obj.browse(cr, uid,
                                              context['active_ids'], context):
                amount += invoice.amount_total
            data['amount'] = amount
            data['breakdown_type'] = 'cost_price'
        return data

    _columns = {
        'amount': fields.float('Amount',
                               digits_compute=dp.get_precision('Account')),
        'breakdown_type': fields.selection([
                ('cost_price', 'By Cost Price'),
                ('quantity', 'By Quantity'),
            ], 'Breakdown type'),
        'breakdown_line_ids': fields.one2many('invoice.cost.breakdown.line',
                                          'breakdown_id', 'Breakdown lines'),
        'invoice_ids': fields.many2many('account.invoice',
                                        'invoice_cost_breakdown_rel',
                                        'breakdown_id',
                                        'invoice_id'
                               'Invoices',
                               domain=[('type', '=', 'in_invoice'),
                                       ('state', 'in', ['open', 'paid'])]),
        'state': fields.selection([
                ('step1', 'Step 1'),
                ('step2', 'Step 2'),
            ], 'State', readonly=True),
    }

    def next_step(self, cr, uid, ids, context=None):
        ''' Create each line of each invoice selected in the breakdown line 
            wizard and put products, quantities and price costs in each ones.
            @param self: This object
            @param cr: Data base cursor
            @param uid: User identifier
            @param ids: Object identifier
            @param context: default context of the record
            @return: True
        '''
        if context is None:
            context = {}
        breakdown_line_obj = self.pool.get('invoice.cost.breakdown.line')
        for breakdown in self.browse(cr, uid, ids, context):
            for invoice_id in breakdown.invoice_ids:
                move_lines = invoice_id.invoice_line
                for line in move_lines:
                    product_id = line.product_id and line.product_id.id \
                                    or False
                    breakdown_line_values = {
                        'product_id': product_id,
                        'quantity': line.quantity or 0,
                        'price_cost': line.price_unit or 0,
                        'breakdown_id': breakdown.id,
                    }
                    breakdown_line_values['price_subtotal'] = \
                                    breakdown_line_values['quantity'] * \
                                    breakdown_line_values['price_cost']
                    breakdown_line_obj.create(cr, uid,
                                              breakdown_line_values, context)
        values = {
            'state': 'step2',
        }
        return self.write(cr, uid, ids, values, context)

    def go_back(self, cr, uid, ids, context=None):
        ''' Returns to previous step of the wizard.
            @param self: This object
            @param cr: Data base cursor
            @param uid: User identifier
            @param ids: Object identifier
            @param context: default context of the record
            @return: True
        '''
        if context is None:
            context = {}
        breakdown_line_obj = self.pool.get('invoice.cost.breakdown.line')
        breakdown_line_ids = breakdown_line_obj.search(cr, uid, [],
                                                       context=context)
        breakdown_line_obj.unlink(cr, uid, breakdown_line_ids, context)
        return self.write(cr, uid, ids, {'state': 'step1'}, context)

    def compute_lines(self, cr, uid, ids, context=None):
        """ Compute price_subtotal, percent, and amount fields of 
            invoice.cost.breakdown.line
            @param self: This object
            @param cr: Data base cursor
            @param uid: User identifier
            @param ids: List of identifier objects
            @param context: default context of the record
            @return: True
        """
        if context is None:
            context = {}
        breakdown = self.browse(cr, uid, ids, context)[0]
        line_obj = self.pool.get('invoice.cost.breakdown.line')
        line_ids = line_obj.search(cr, uid,
                        [('breakdown_id', '=', breakdown.id)], context=context)
        if breakdown.breakdown_type == 'quantity':
            line_obj.compute_by_quantity(cr, uid, line_ids,
                                    breakdown.amount, context=context)
        else:
            line_obj.compute_by_subtotal(cr, uid, line_ids,
                                    breakdown.amount, context=context)
        return True

    def compute(self, cr, uid, ids, context=None):
        """ Compute the new average price of the products
            @param self: This object
            @param cr: Data base cursor
            @param uid: User identifier
            @param ids: List of identifier objects
            @param context: default context of the record
            @return: True
        """
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('invoice.cost.breakdown.line')
        breakdown = self.browse(cr, uid, ids, context)[0]
        self.compute_lines(cr, uid, ids, context)
        line_ids = line_obj.search(cr, uid,
                        [('breakdown_id', '=', breakdown.id)], context=context)
        for breakdown_line in line_obj.browse(cr, uid, line_ids,
                                                            context=context):
            if not breakdown_line.product_id:
                continue
            product = breakdown_line.product_id
            if product.product_tmpl_id.cost_method != 'average':
                continue
            standar_price = product.product_tmpl_id.standard_price
            quantity = breakdown_line.quantity
            unit_cost = breakdown_line.amount / quantity
            stock_qty = product.qty_available
            if stock_qty <= 0:
                # Don't change standard price
                new_price = standar_price
            elif stock_qty - quantity <= 0:
                # There are less products than invoiced ones
                new_price = standar_price + unit_cost
            else:
                new_price = ((stock_qty - quantity) * standar_price + \
                        quantity * (standar_price + unit_cost)) / \
                        stock_qty
            product_obj.write(cr, uid, [product.id],
                              {'standard_price': new_price})
        return {'type': 'ir.actions.act_window_close'}

invoice_cost_breakdown()


class invoice_cost_breakdown_line(osv.osv_memory):
    """
    This class add lines to the invoice_cost_breakdown class.
    """

    _name = "invoice.cost.breakdown.line"

    _columns = {
        'breakdown_id': fields.many2one('invoice.cost.breakdown', 'Breakdown'),
        'product_id':fields.many2one('product.product', 'Product',
                        readonly=True),
        'quantity': fields.float('Quantity',
                        digits_compute=dp.get_precision('Account')),
        'price_cost': fields.float('Cost Price',
                        digits_compute=dp.get_precision('Account')),
        'price_subtotal': fields.float('Subtotal Price',
                        digits_compute=dp.get_precision('Account'),
                        readonly=True),
        'percent': fields.float('Cost Percent',
                        digits_compute=dp.get_precision('Account'),
                        readonly=True),
        'amount': fields.float('Cost Amount',
                        digits_compute=dp.get_precision('Account'),
                        readonly=True),
    }

    def onchange_price(self, cr, uid, ids, *args):
        """Description of the method
            @param self: this object
            @param cr: cursor
            @param uid: user identifier
            @param args: fields passed as arguments to method from view
            @param args[0]: quantity
            @param args[1]: price_cost
            @return: new price_subtotal value
        """
        res = {}
        res['value'] = {}
        quantity = args[0]
        price_cost = args[1]
        val = {
            'price_subtotal': price_cost * quantity
        }
        self.write(cr, uid, ids, val)
        res['value']['price_subtotal'] = val['price_subtotal']
        return res

    def compute_by_quantity(self, cr, uid, ids, amount, context=None):
        """ Compute price_subtotal, percent, and amount fields of 
            invoice.cost.breakdown.line by quantity method
            @param self: this object
            @param cr: cursor
            @param uid: user identifier
            @param amount: amount to breakdown
            @param context: default context of the record
            @return: True
        """
        if context is None:
            context = {}
        lines = self.browse(cr, uid, ids, context)
        amount_qty = 0.0
        for line in lines:
            amount_qty += line.quantity
        if amount_qty <= 0:
            return True
        values = {}
        for line in lines:
            values['percent'] = line.quantity * 100 / amount_qty
            values['amount'] = values['percent'] * amount / 100
            self.write(cr, uid, [line.id], values, context)
        return True

    def compute_by_subtotal(self, cr, uid, ids, amount, context=None):
        """ Compute price_subtotal, percent, and amount fields of 
            invoice.cost.breakdown.line by subtotal method
            @param self: this object
            @param cr: cursor
            @param uid: user identifier
            @param amount: amount to breakdown
            @param context: default context of the record
            @return: True
        """
        if context is None:
            context = {}
        lines = self.browse(cr, uid, ids, context)
        amount_subtotal = 0.0
        subtotal = {}
        for line in lines:
            subtotal[line.id] = self.onchange_price(cr, uid, [line.id],
                            line.quantity,
                            line.price_cost)['value']['price_subtotal']
            amount_subtotal += subtotal[line.id]
        values = {}
        if amount_subtotal == 0.0:
            return True
        for line in lines:
            values['amount'] = subtotal[line.id] * amount / amount_subtotal
            values['percent'] = values['amount'] * 100 / amount
            self.write(cr, uid, [line.id], values, context)
        return True

invoice_cost_breakdown_line()
