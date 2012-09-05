# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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

from osv import fields, osv
import decimal_precision as dp

class sale_shop(osv.osv):
    _inherit = 'sale.shop'

    _columns = {
        'special_price': fields.boolean('Apply Special Price'),
        'type_special_price': fields.selection([('price','Special Price'),('pricelist','Special Pricelist')], 'Price'),
        'special_pricelist_id': fields.many2one('product.pricelist', 'Special Pricelist'),
    }

    _defaults = {
        'type_special_price': 'price',
    }

sale_shop()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)

        if product:
            sale_shop_obj = self.pool.get('sale.shop')
            user = self.pool.get('res.users').browse(cr, uid, uid)

            if user.shop_id.special_price:
                prod = self.pool.get('product.product').browse(cr, uid, product)
                if user.shop_id.type_special_price == 'pricelist' and user.shop_id.special_pricelist_id:
                    special_price = self.pool.get('product.pricelist').price_get(cr, uid, [user.shop_id.special_pricelist_id.id], prod.id, 1.0)[user.shop_id.special_pricelist_id.id]
                else:
                    special_price = prod.special_price

                price_unit = res['value']['price_unit']
                
                if special_price > 0.0 and special_price < price_unit:
                    res['value']['price_unit'] = special_price

        return res

sale_order_line()
