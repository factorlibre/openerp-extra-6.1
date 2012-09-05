# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields
from osv import osv
import ir

import netsvc
import time
from mx import DateTime
from tools.translate import _

class mrp_flow(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = 'mrp.production'
    
    def _check_states(self, cr, uid, ids=False, context={}):
        result = True
        move_pool = self.pool.get('stock.move')
        
        if not ids:
            ids = self.search(cr, uid, [('state','=','confirmed')])
            
        for po in self.browse(cr, uid, ids):
            for line in po.move_lines:
                id = move_pool.search(cr, uid, [('picking_id','=',po.picking_id.id),('product_id','=',line.product_id.id)])
                state = move_pool.browse(cr, uid, id)[0].state
                if state == 'confirmed':
                    state = 'waiting'
                move_pool.write(cr, uid, [line.id], {'state':state})
        cr.commit()
        return result
mrp_flow()

class mrp_procurement(osv.osv):
    _inherit = 'mrp.procurement'

    def _procure_confirm(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        res = super(mrp_procurement, self)._procure_confirm(cr, uid, ids, use_new_cursor, context)
        self.pool.get('mrp.production')._check_states(cr, uid, context=context)
        return res
        
mrp_procurement()
