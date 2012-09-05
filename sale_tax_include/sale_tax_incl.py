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

import time
import netsvc
from osv import fields, osv
import ir

class sale_order(osv.osv):
    _inherit = "sale.order"
    def _amount_line_tax(self, cr, uid, line, context=None):
        return line.price_subtotal_incl - line.price_subtotal

    _columns = {
        'price_type': fields.selection([
            ('tax_included', 'Tax included'),
            ('tax_excluded', 'Tax excluded')
        ], 'Price method', required=True),
    }
    _defaults = {
        'price_type': lambda * a: 'tax_excluded',
    }
    def _inv_get(self, cr, uid, order, context=None):
        return {
            'price_type': order.price_type
        }
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    def _amount_line2(self, cr, uid, ids, name, args, context=None):
        """
        Return the subtotal excluding taxes with respect to price_type.
        """
        res = {}
        tax_obj = self.pool.get('account.tax')
        res_init = super(sale_order_line, self)._amount_line(cr, uid, ids, name,
            args, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'price_subtotal': 0.0,
                'price_subtotal_incl': 0.0,
                'data': []
            }
            if not line.product_uom_qty:
                continue
            if line.order_id:
                product_taxes = []
                if line.product_id:
                    product_taxes = filter(lambda x: x.price_include,
                        line.product_id.taxes_id)

                if (
                    (set(product_taxes) == set(line.tax_id))
                    or not product_taxes) and (
                    line.order_id.price_type == 'tax_included'
                    ):
                    res[line.id]['price_subtotal_incl'] = res_init[line.id]
                else:
                    res[line.id]['price_subtotal'] = res_init[line.id]
                    for tax in tax_obj.compute_inv(cr, uid, product_taxes,
                        res_init[line.id] / line.product_uom_qty,
                        line.product_uom_qty
                    ):
                        res[line.id]['price_subtotal'] = (
                            res[line.id]['price_subtotal']
                                - round(tax['amount'], 2)
                            )
            else:
                res[line.id]['price_subtotal'] = res_init[line.id]

            if res[line.id]['price_subtotal']:
                res[line.id]['price_subtotal_incl'] = res[line.id]['price_subtotal']
                for tax in tax_obj.compute(cr, uid, line.tax_id,
                    res[line.id]['price_subtotal'] / line.product_uom_qty,
                    line.product_uom_qty
                ):
                    res[line.id]['price_subtotal_incl'] = (
                        res[line.id]['price_subtotal_incl'] + tax['amount'])
                    res[line.id]['data'].append(tax)
            else:
                res[line.id]['price_subtotal'] = res[line.id]['price_subtotal_incl']
                for tax in tax_obj.compute_inv(cr, uid, line.tax_id,
                    res[line.id]['price_subtotal_incl'] / line.product_uom_qty,
                    line.product_uom_qty
                ):
                    res[line.id]['price_subtotal'] = res[line.id]['price_subtotal'] - tax['amount']
                    res[line.id]['data'].append(tax)

            res[line.id]['price_subtotal'] = round(res[line.id]['price_subtotal'], 2)
            res[line.id]['price_subtotal_incl'] = round(res[line.id]['price_subtotal_incl'], 2)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for inv in self.pool.get('sale.order').browse(cr, uid, ids,
                context=context):
            for line in inv.order_line:
                result[line.id] = True
        return result.keys()
    _columns = {
        'price_subtotal': fields.function(_amount_line2, method=True,
            string='Subtotal w/o tax', multi='amount',
            store={
                'sale.order' : (_get_order, ['price_type'], 5),
                'sale.order.line' : (lambda self, cr, uid, ids, context=None: ids, None, 5)
            }),
        'price_subtotal_incl' : fields.function(_amount_line2, method=True,
            string='Subtotal', multi='amount',
            store={
                'sale.order' : (_get_order, ['price_type'], 5),
                'sale.order.line' : (lambda self, cr, uid, ids, context=None: ids, None, 5)
            }),
    }
sale_order_line()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _description = "Picking list"

    def action_invoice_create(self, cursor, user, ids, journal_id=False,
           group=False, type='out_invoice', context=None):
       return_dict = super(stock_picking, self).action_invoice_create(cursor,
           user, ids, journal_id=journal_id, group=group, type=type,
           context=context)
       sale_obj = self.pool.get('sale.order')
       invoice_obj = self.pool.get('account.invoice')

       for picking in self.browse(cursor, user, ids, context=context):
           sale_ids = sale_obj.search(cursor, user, [('name', '=', picking.origin)],
                context=context)
       for line in sale_obj.read(cursor, user, sale_ids, ['price_type']):
           for id in ids:
               invoice_obj.write(cursor, user, return_dict[id],
                   {'price_type': line['price_type']}, context=context)
               invoice_obj.button_compute(cursor, user, [return_dict[id]],
                   context=context)
       return return_dict

stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
