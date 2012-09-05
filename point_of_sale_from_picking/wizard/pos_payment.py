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

class pos_make_payment(osv.osv_memory):
    _inherit = 'pos.make.payment'

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        super(pos_make_payment, self).view_init(cr, uid, fields_list, context=context)
        active_id = context and context.get('active_id', False) or False
        if active_id:
            order = self.pool.get('pos.order').browse(cr, uid, active_id, context=context)

            partner_id = order.partner_id and order.partner_id or False
            if not partner_id:
                partner_id = order.partner_id or False

            ''' Check if the partner has other pickings with the same products'''
            pos_warn_sale_order = order.pos_warn_sale_order or False
            if pos_warn_sale_order and partner_id:
                address_ids = [adr.id for adr in partner_id.address]
                picking_obj = self.pool.get('stock.picking')
                picking_ids = picking_obj.search(cr, uid, [
                        ('state', 'in', ['auto','confirmed','assigned']),
                        ('id', '!=', order.picking_id.id),
                        ('address_id', 'in', address_ids),
                    ])
                if picking_ids:
                    product_ids = [line.product_id.id for line in order.lines]
                    for picking in picking_obj.browse(cr, uid, picking_ids, context):
                        for m in picking.move_lines:
                            if m.product_id.id in product_ids:
                                product = (m.product_id.name).encode('utf-8')
                                sale_order_info = (picking.origin and picking.name + '-' + picking.origin or picking.name).encode('utf-8')
                                raise osv.except_osv(_('Warning! Product already ordered'),
                                    _("Product %s is already ordered in picking %s." \
                                    " If you want to order it again ignoring this picking,"\
                                    " you must uncheck the boolean field"\
                                    " 'Product in sale order warning'.") % (product, sale_order_info))
        return True

pos_make_payment()
