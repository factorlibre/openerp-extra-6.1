# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LTDA.
#    authors: Raphaël Valyi
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

from osv import fields, osv

from tools.translate import _

class stock_batch_process(osv.osv_memory):

    _name = "stock.batch.process"
    _description = "Stock Batch Process"

    _columns = {
        'force_availability': fields.boolean('Force availability if not availble?', help='That will lead to abnormal negative stock values'),
    }

    def process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date'])
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking
            onshipdata_obj[ids] = onshipdata_obj.new_picking
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        active_ids = context.get('active_ids', [])
        active_pickings = picking_pool.browse(cr, uid, context.get('active_id', False), context=context)
        pick_type = picking_pool.read(cr, uid, [active_ids[0]], ['type'])[0]['type']
        for id in active_ids:
            if self.read(cr, uid, ids, ['force_availability'])[0]['force_availability'] and picking_pool.read(cr, uid, [id], ['state'])[0]['state'] == 'confirmed':
                picking_pool.force_assign(cr, uid, active_ids, context)
            picking_pool.action_move(cr, uid, active_ids, context)
        action = {}
        if pick_type == 'in':
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
        if pick_type == 'out':
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        else:
            action_model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'action_picking_tree6')

        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        action['domain'] = "[('state','!=','assigned'), ('id','in', ["+','.join(map(str, active_ids))+"])]"
        return action

stock_batch_process()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
