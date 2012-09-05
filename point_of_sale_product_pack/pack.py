# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#
#    Based on the work of nan_product_pack:
#    Copyright (c) 2009 Àngel Àlvarez - NaN  (http://www.nan-tic.com) All Rights Reserved.
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

import math
from osv import fields, osv
from tools.translate import _

class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'
    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'pack_depth': fields.integer('Depth', required=True, help='Depth of the product if it is part of a pack.'),
        'pack_parent_line_id': fields.many2one('pos.order.line', 'Pack', help='The pack that contains this product.'),
        'pack_child_line_ids': fields.one2many('pos.order.line', 'pack_parent_line_id', 'Lines in pack', help=''),
    }
    _defaults = {
        'pack_depth': lambda *a: 0,
        'sequence': lambda *a: 10,
    }
    _order = 'sequence, id asc'
pos_order_line()

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def create(self, cr, uid, vals, context=None):
        result = super(pos_order,self).create(cr, uid, vals, context)
        self.expand_packs(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(pos_order,self).write(cr, uid, ids, vals, context)
        self.expand_packs(cr, uid, ids, context)
        return result

    def expand_packs(self, cr, uid, ids, context={}, depth=1):
        if depth == 10:
            return
        updated_orders = []
        if not isinstance(ids, list):
            ids = [ids]
        pos_line_obj = self.pool.get('pos.order.line')
        pos_order = self.browse(cr, uid, ids[0], context)
        pricelist_id = pos_order.shop_id.pricelist_id and \
                                pos_order.shop_id.pricelist_id.id or False
        partner_id = pos_order.partner_id and pos_order.partner_id.id or \
                                                                    False

        for order in self.browse(cr, uid, ids, context):

            # The reorder variable is used to ensure lines of the same pack go right after their
            # parent.
            # What the algorithm does is check if the previous item had children. As children items
            # must go right after the parent if the line we're evaluating doesn't have a parent it
            # means it's a new item (and probably has the default 10 sequence number - unless the
            # appropiate c2c_pos_sequence module is installed). In this case we mark the item for
            # reordering and evaluate the next one. Note that as the item is not evaluated and it might
            # have to be expanded it's put on the queue for another iteration (it's simple and works well).
            # Once the next item has been evaluated the sequence of the item marked for reordering is updated
            # with the next value.
            sequence = -1
            reorder = []
            last_had_children = False
            for line in order.lines:
                if last_had_children and not line.pack_parent_line_id:
                    reorder.append( line.id )
                    if line.product_id.pack_line_ids and not order.id in updated_orders:
                        updated_orders.append( order.id )
                    continue

                sequence += 1

                if sequence > line.sequence:
                    pos_line_obj.write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence

                if not line.product_id:
                    continue

                # If pack was already expanded (in another create/write operation or in
                # a previous iteration) don't do it again.
                if line.pack_child_line_ids:
                    last_had_children = True
                    continue
                last_had_children = False

                for subline in line.product_id.pack_line_ids:
                    sequence += 1

                    subproduct = subline.product_id
#                    quantity = subline.quantity * line.product_uom_qty
                    quantity = subline.quantity * line.qty

                    if line.product_id.pack_fixed_price:
                        discount = 100.0
                        notice = _('Included in pack')
                    else:
                        discount = line.discount
                        notice = line.notice

                    # Obtain product name in partner's language
                    ctx = {'lang': order.partner_id.lang}
                    subproduct_name = self.pool.get('product.product').browse(cr, uid, subproduct.id, ctx).name

                    vals = {
                        'sequence': sequence,
                        'order_id': order.id,
                        'name': '%s%s' % ('> '* (line.pack_depth+1), subproduct_name),
                        'product_id': subproduct.id,
                        'discount': discount,
                        'notice': notice,
                        'qty': quantity,
                        'pack_parent_line_id': line.id,
                        'pack_depth': line.pack_depth + 1,
                    }

                    vals['price_unit2'] = pos_line_obj.price_by_product(cr,
                                    uid, [], pricelist_id, subproduct.id,
                                    quantity, partner_id)

                    pos_line_obj.create(cr, uid, vals, context)
                    if not order.id in updated_orders:
                        updated_orders.append( order.id )

                for id in reorder:
                    sequence += 1
                    pos_line_obj.write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)

        if updated_orders:
            # Try to expand again all those orders that had a pack in this iteration.
            # This way we support packs inside other packs.
            self.expand_packs(cr, uid, ids, context, depth+1)
        return

pos_order()
