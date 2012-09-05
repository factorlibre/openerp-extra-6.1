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


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_move_create(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_move_create(cr, uid, ids, args)
        product_obj = self.pool.get('product.product')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice = self.browse(cr, uid, ids)[0]
        if invoice.type not in ('in_invoice', 'in_refund'):
            return res
        for line in invoice.invoice_line:
            if line.product_id and \
                    line.product_id.product_tmpl_id.cost_method == 'average':
                standard_price = line.product_id.product_tmpl_id.standard_price
                qty_available = line.product_id.qty_available

                if invoice.type == 'in_invoice':
                    if qty_available - line.quantity_picking + line.quantity <= 0:
                        # Returning all products to supplier we not change the std price
                        new_std_price = standard_price
                    else:
                        # standard price = available - picking + invoice
                        new_std_price = ((standard_price * qty_available) - \
                           (line.price_unit_picking * line.quantity_picking) + \
                           (line.price_unit * line.quantity)) / \
                           (qty_available - line.quantity_picking + line.quantity)

                elif invoice.type == 'in_refund':
                    if qty_available + line.quantity_picking - line.quantity <= 0:
                        # Sending all products to supplier we not change the std price
                        new_std_price = standard_price
                    else:
                        # standard price = available + picking - invoice
                        new_std_price = ((standard_price * qty_available) + \
                           (line.price_unit_picking * line.quantity_picking) - \
                           (line.price_unit * line.quantity)) / \
                           (qty_available + line.quantity_picking - line.quantity)

                if new_std_price <= 0:
                    # Returning products to supplier we can get negative prices.
                    # In this case we not change the std price
                    new_std_price = standard_price

                value = {
                    'standard_price': new_std_price,
                }
                product_obj.write(cr, uid, line.product_id.id, value)
                value = {
                    'price_unit_picking': line.price_unit,
                    'quantity_picking': line.quantity,
                }
                invoice_line_obj.write(cr, uid, line.id, value)

        return res

account_invoice()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
        'price_unit_picking': fields.float('Unit Price Picking', required=True,
                                digits_compute=dp.get_precision('Account')),
        'quantity_picking': fields.float('Quantity Picking', required=True),
    }

account_invoice_line()
