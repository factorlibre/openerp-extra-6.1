# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_bundle_product for OpenERP                                            #
# Copyright (c) 2011 CamptoCamp. All rights reserved. @author Joel Grand-Guillaume #
# Copyright (c) 2011 Akretion. All rights reserved. @author Sébastien BEAU      #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc


class sale_order(osv.osv):
    
    _inherit = "sale.order"
        
    def add_a_new_line(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'view_order_line_form']], context=context)
        if ir_model_data_id:
            res_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']        
        
        sale_order = self.browse(cr, uid, ids[0], context=context)
        ctx = {
            'order_id': ids and ids[0],
            'partner_id': sale_order.partner_id.id,
            'pricelist': sale_order.pricelist_id.id,
            'shop': sale_order.shop_id.id,
            'date_order': sale_order.date_order,
            'fiscal_position': sale_order.fiscal_position.id,
        }
        
        
        return {
            'name': 'Sale Order Line',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'sale.order.line',
            'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
    
    
    
sale_order()
    



class sale_order_line(osv.osv):
    
    _inherit = "sale.order.line"

    def save_and_close(self, cr, uid, ids, context):
        return {}
    
    def save_and_continue(self, cr, uid, ids, context):
        res = self.pool.get('sale.order').add_a_new_line(cr, uid, [context['order_id']], context=None)
        res['nodestroy']=False
        return res
    
    def create(self, cr, uid, vals, context=None):
        if not context:
            context={}
        if context.get('order_id', False):
            vals['order_id']= context['order_id']
        res = super(sale_order_line, self).create(cr, uid, vals, context=context)
        if context.get('order_id', False):
            context['create_sale_order_line_id']=res
        return res
    
    def action_configure_product(self, cr, uid, ids, context=None):
        if not ids:
            return False
        if not context:
            context = {}
        return {
            'name': 'Product Configuration',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.item.set.configurator',
            'context': "{'order_line_id': %s}"%(ids[0]),
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        } 
        
    _columns = {
        'so_line_item_set_ids':fields.many2many('sale.order.line.item.set', 'so_line_so_item_set_rel','sale_order_line_id', 'so_item_set_id','Choosen configurtion'),
    }


sale_order_line()

