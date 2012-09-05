# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_bundle_product for OpenERP                                            #
# Copyright (c) 2011 Akretion. All rights reserved. @author Sébastien BEAU      #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


from osv import osv, fields
from tools.translate import _
import netsvc

class procurement_order(osv.osv):

    _inherit = "procurement.order"
    
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line, context=None):
        line['so_line_item_set_ids'] = [(6,0, [x.id for x in procurement.so_line_item_set_ids])]
        return super(procurement_order, self).create_procurement_purchase_order(cr, uid, id, po_vals, line, context=context)
    
    def _get_sale_order_line_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        for id in ids:
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, [['procurement_id', '=', id]], context=context)
            if sale_order_line_ids:
                res[id] = sale_order_line_ids[0]
            else:
                res[id] = False
        return res
    
    _columns = {
        'sale_order_line_id': fields.function(_get_sale_order_line_id, type="many2one", relation='sale.order.line', string='Sale Order Line', readonly=True, method=True),
        'so_line_item_set_ids': fields.related('sale_order_line_id', 'so_line_item_set_ids', type='many2many', relation='sale.order.line.item.set', string='Choosen configuration'),
    }
    
procurement_order()
