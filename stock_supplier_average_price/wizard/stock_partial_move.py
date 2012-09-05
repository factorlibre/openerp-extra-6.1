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

class stock_partial_move(osv.osv_memory):
    _inherit = "stock.partial.move"

    def __create_partial_move_memory(self, move):
        move_memory = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty,
            'product_uom' : move.product_uom.id,
            'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
        }

        picking_name = move.picking_id.name
        picking_type = move.picking_id.type
        if picking_type == 'in' and '-return' not in picking_name\
                    or picking_type == 'out'  and '-return' in picking_name:
            move_memory.update({
                'cost' : move.product_id.standard_price,
                'currency' : move.product_id.company_id and \
                            move.product_id.company_id.currency_id and move.product_id.company_id.currency_id.id or False,
            })
        return move_memory

    def __get_picking_type(self, cr, uid, move_ids):
        move_obj = self.pool.get('stock.move')
        for move in move_obj.browse(cr, uid, move_ids):
            return_picking = move.picking_id and move.picking_id.name and \
                                    '-return' in move.picking_id.name or False
            picking_type = move.picking_id and move.picking_id.type or \
                                    False
            cost_method = move.product_id.cost_method
            if picking_type == 'in' and cost_method == 'average' and \
                                    not return_picking:
                picking_type = 'product_moves_in'
                break
            elif picking_type == 'out' and cost_method == 'average' and \
                                    return_picking:
                picking_type = 'product_moves_in'
                break
            else:
                picking_type = 'product_moves_out'
        return picking_type

    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """

        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')

        move_ids = context.get('active_ids', False)
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_datas = {
            'delivery_date' : partial.date
        }

        p_moves = {}
        picking_type = self.__get_picking_type(cr, uid, move_ids)

        moves_list = picking_type == 'product_moves_in' and \
                        partial.product_moves_in  or partial.product_moves_out
        for product_move in moves_list:
            p_moves[product_move.move_id.id] = product_move

        moves_ids_final = []
        for move in move_obj.browse(cr, uid, move_ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            if not p_moves.get(move.id):
                continue
            partial_datas['move%s' % (move.id)] = {
                'product_id' : p_moves[move.id].product_id.id,
                'product_qty' : p_moves[move.id].quantity,
                'product_uom' :p_moves[move.id].product_uom.id,
                'prodlot_id' : p_moves[move.id].prodlot_id.id,
            }

            moves_ids_final.append(move.id)
            if (picking_type == 'product_moves_in') and \
                        (move.product_id.cost_method == 'average'):
                partial_datas['move%s' % (move.id)].update({
                    'product_price' : p_moves[move.id].cost,
                    'product_currency': p_moves[move.id].currency.id,
                })

        move_obj.do_partial(cr, uid, moves_ids_final, partial_datas,
                                                            context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_partial_move()
