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


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    # Removed readonly attribute to allow to invoice any stock picking
    # (for example, if someone deletes by mistake the invoice of invoiced picking)
    _columns = {
        'invoice_state': fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Control",
            select=True, required=True),
        'client_order_ref': fields.char('Customer Reference', size=64),
    }
    _order = 'date desc, id'

    def _get_price_unit_invoice(self, cr, uid, move_line, invoice_type, context=None):
        """ Gets price unit for invoice
        IN pickings: Gets the price unit of the picking instead of the cost price of the product
        @param move_line: Stock move lines
        @param invoice_type: Type of invoice
        @return: The price unit for the move line
        """
        if context is None:
            context = {}

        if invoice_type in ('in_invoice', 'in_refund'):
            # Take the user company and pricetype
            context['currency_id'] = move_line.company_id.currency_id.id
            # Gets the price unit of the picking instead of the cost price of the product
            amount_unit = move_line.price_unit
            return amount_unit

        elif move_line.sale_line_id and move_line.sale_line_id.product_id.id == move_line.product_id.id:
            uom_id = move_line.product_id.uom_id.id
            uos_id = move_line.product_id.uos_id and move_line.product_id.uos_id.id or False
            price = move_line.sale_line_id.price_unit
            coeff = move_line.product_id.uos_coeff
            if uom_id != uos_id  and coeff != 0:
                price_unit = price / coeff
                return price_unit
            return move_line.sale_line_id.price_unit

        else:
            return move_line.product_id.list_price

stock_picking()
