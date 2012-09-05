# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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
from tools.translate import _

class pos_sale_get(osv.osv_memory):
    _name = 'pos.sale.get'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True),
    }

    _defaults = {
        'partner_id': lambda self, cr, uid, context:
            self.pool.get('pos.order').browse(cr, uid, context['active_id'], context).partner_id.id,
    }

    def sale_complete(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        pick_obj = self.pool.get('stock.picking')
        pos_order_obj = self.pool.get('pos.order')
        pos_order_line_obj = self.pool.get('pos.order.line')

        pos_sale_get = self.browse(cr, uid, ids[0], context)
        picking_id = pos_sale_get.picking_id

        order = pos_order_obj.browse(cr, uid, context['active_id'], context)

        if order.state in ('paid', 'invoiced'):
            raise wizard.except_wizard(_('UserError'), _("You can't modify this order. It has already been paid"))

        pick = pick_obj.browse(cr, uid, picking_id.id, context)

        pos_order_obj.write(cr, uid, context['active_id'], {
            'picking_id': picking_id.id,
            'partner_id': pick.address_id and pick.address_id.partner_id.id,
        }, context)

        order = pick_obj.write(cr, uid, picking_id.id, {
            'invoice_state': 'none',
            'pos_order': context['active_id'],
        }, context)

        for line in pick.move_lines:
            pos_order_line_obj.create(cr, uid, {
                'name': line.sale_line_id.name,
                'order_id': context['active_id'],
                'qty': line.product_qty,
                'product_id': line.product_id.id,
                'price_unit': line.sale_line_id.price_unit,
                'discount': line.sale_line_id.discount,
            })

        return {}

pos_sale_get()
