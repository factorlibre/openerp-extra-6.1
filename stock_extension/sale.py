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
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

class sale_order(osv.osv):
    _inherit = "sale.order"

    def action_ship_create(self, cr, uid, ids, *args):
        """ This method inherit super action_ship_create method to add 
            client_order_ref sale field to stock_picking model
            @param self: The object pointer
            @param cr: The current row, from the database cursor,
            @param uid: The current user’s ID for security checks,
            @param ids: List of registers’ IDs
            @param *args: Not used
            @return: True
        """
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr, uid, ids, context={}):
            pids = [x.id for x in order.picking_ids]
            picking_obj.write(cr, uid, pids, {
                'client_order_ref': order.client_order_ref
            })
        return result

sale_order()
