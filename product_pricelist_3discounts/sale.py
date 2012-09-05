# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Raimon Esteve <resteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
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

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _name = 'sale.order.line'
    _columns = {
        'discount_description': fields.char('Disc. Name', size=32),
    }

    def product_id_change(self, cr, uid, ids, pricelist_id, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):

        pricelist_obj = self.pool.get('product.pricelist')
        res = super(sale_order_line, self).product_id_change(cr, uid, ids,
                pricelist_id, product_id, qty, uom, qty_uos, uos, name,
                partner_id, lang, update_tax, date_order,
                fiscal_position=fiscal_position, flag=flag)
        if product_id:
            res['value']['discount_description'] = pricelist_obj.\
                    price_description_get(cr, uid,
                    [pricelist_id], product_id, qty or 1.0,
                    context={'uom': uom, 'date': date_order })

        return res

    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_line_ids = super(sale_order_line, self).\
                    invoice_line_create(cr, uid, ids, context)
        for invoice_line in invoice_line_obj.browse(cr, uid,
                                                    invoice_line_ids, context):
            order_line_ids = self.search(cr, uid, [
                        ('invoice_lines', '=', invoice_line.id)],
                        context=context)
            order_line = self.browse(cr, uid, order_line_ids, context)[0]
            value = {
                'discount_description': order_line.discount_description
            }
            invoice_line_obj.write(cr, uid, invoice_line.id, value, context)
        return invoice_line_ids

sale_order_line()
