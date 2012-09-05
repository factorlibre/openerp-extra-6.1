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

from osv import osv

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def get_picking_type(self, cr, uid, picking, context=None):
        picking_type = picking.type
        return_picking = picking.name and '-return' in picking.name or False
        for move in picking.move_lines:
            if picking.type == 'in' and move.product_id.cost_method == \
                                            'average' and not return_picking:
                picking_type = 'in'
                break
            elif picking.type == 'out' and move.product_id.cost_method == \
                                            'average' and return_picking:
                picking_type = 'in'
                break
            else:
                picking_type = 'out'
        return picking_type

stock_partial_picking()
