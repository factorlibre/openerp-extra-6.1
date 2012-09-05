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

from osv import osv, fields


class stock_partial_move_memory_out(osv.osv_memory):
    ''' This field is added to allow searches by user_id in osv_memory 
        object, to clear buffer of osv.memory if previous process wizard of
        warehouse management or product moves are cancelled, otherwise
        previous lines of picking are added to the current wizard.
    '''
    _inherit = "stock.move.memory.out"
    _columns = {
        'user_id' : fields.many2one('res.user', string="User", required=True),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

stock_partial_move_memory_out()


class stock_partial_move_memory_in(osv.osv_memory):
    ''' This field is added to allow searches by user_id in osv_memory 
        object, to clear buffer of osv.memory if previous process wizard of
        warehouse management or product moves are cancelled, otherwise
        previous lines of picking are added to the current wizard.
    '''
    _inherit = "stock.move.memory.in"
    _columns = {
        'user_id' : fields.many2one('res.user', string="User", required=True),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

stock_partial_move_memory_in()


class stock_partial_move(osv.osv_memory):
    _inherit = "stock.partial.move"

    def __get_active_stock_moves(self, cr, uid, context=None):
        ''' Clear buffer of osv.memory if previous process wizard of warehouse
            management is cancelled, otherwise previous lines of picking are
            added to the current wizard.
        '''
        if context is None:
            context = {}

        memory_out_obj = self.pool.get("stock.move.memory.out")
        memory_out_ids = memory_out_obj.search(cr, uid, [('user_id', '=', uid)],
                                                                    context)
        memory_out_obj.unlink(cr, uid, memory_out_ids, context)

        memory_in_obj = self.pool.get("stock.move.memory.in")
        memory_in_ids = memory_in_obj.search(cr, uid, [('user_id', '=', uid)],
                                                                    context)
        memory_in_obj.unlink(cr, uid, memory_in_ids, context)

        return super(stock_partial_move, self).__get_active_stock_moves(cr, uid,
                                                                    context)

    _defaults = {
        'product_moves_in' : __get_active_stock_moves,
        'product_moves_out' : __get_active_stock_moves,
    }

stock_partial_move()
