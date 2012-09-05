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

    def default_get(self, cr, uid, fields, context=None):
        ''' Clear buffer of osv.memory if previous process wizard of product
            moves is cancelled, otherwise previous line of pinking is added to
            the current wizard.
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

        return super(stock_partial_picking, self).default_get(cr, uid, fields,
                                                                    context)

stock_partial_picking()
