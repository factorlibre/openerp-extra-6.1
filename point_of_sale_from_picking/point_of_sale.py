# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#        All Rights Reserved,  Jesús Martín <jmartin@zikzakmedia.com>
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

import netsvc
from osv import osv, fields
from tools.translate import _

class pos_order(osv.osv):
    _inherit = 'pos.order'

    _columns = {
        'pos_warn_sale_order': fields.boolean('Product in sale order warning',
            help="Shows a warning if a product added in the POS order has \
already been requested by the partner (the partner has a sale order with \
this product), so the user can decide if is better to do a POS order from \
a sale order."),
    }

    def _get_sale_shop_warning(self, cr, uid, context=None):
        shop_obj = self.pool.get('sale.shop')
        shop_id = self._shop_get(cr, uid, context)
        if shop_id:
            res = shop_obj.browse(cr, uid, shop_id, context).pos_warn_sale_order
            return res
        return False

    _defaults = {
        'pos_warn_sale_order': _get_sale_shop_warning
    }

    def onchange_shop(self, cr, uid, ids, shop_id, context=None):
        result = super(pos_order, self).onchange_shop(cr, uid, ids, shop_id, context)
        shop_obj = self.pool.get('sale.shop')
        pos_warn_sale_order = shop_obj.browse(cr, uid, shop_id, context).pos_warn_sale_order
        result['value']['pos_warn_sale_order'] = pos_warn_sale_order
        return result

pos_order()

