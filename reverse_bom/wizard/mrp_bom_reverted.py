# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
import netsvc

class mrp_reversed_bom(osv.osv_memory):
    _name = "mrp.reversed.bom"
    _description = "Reversed Bom"
    
    _columns = {
    }

    def do_reverse(self, cr, uid, ids, context={}):
        """ To check the product type
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one 
        @param context: A standard dictionary
        @return:  
        """               
        bom_obj = self.pool.get('mrp.bom')
        bom_ids = bom_obj.browse(cr, uid, context['active_ids'])
        mrp_prod_obj = self.pool.get('mrp.production')
        mrp_prodline_obj = self.pool.get('mrp.production.product.line')
        for bom_id in bom_ids:
            production_id = mrp_prod_obj.create(cr, uid, {
                'origin': 'BOM '+ bom_id.name,
                'product_qty': bom_id.product_qty,
                'product_id': bom_id.product_id.id or False,
                'product_uom': bom_id.product_uom.id or False,
                'product_uos_qty': bom_id.product_uos_qty,
                'location_src_id': (bom_id.routing_id and bom_id.routing_id.location_id and bom_id.routing_id.location_id.id) or False,
                'location_dest_id': (bom_id.routing_id and bom_id.routing_id.location_id and bom_id.routing_id.location_id.id) or False,
                'product_uos': bom_id.product_uos.id or False,
                'bom_id': bom_id.id or False,
                'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
            })
            for line in bom_id.bom_lines:
                production_line_id = mrp_prodline_obj.create(cr, uid, {'product_id': line.product_id.id, 
                                                            'name' : line.name,
                                                            'product_qty' : -line.product_qty,
                                                            'product_uom' : line.product_uom.id or False,
                                                            'location_src_id': bom_id.routing_id.location_id.id or bom_id.routing_id.location_id.id or False,
                                                            'location_id': (line.routing_id and line.routing_id.location_id and  line.routing_id.location_id.id) or (bom_id.routing_id and bom_id.routing_id.location_id and bom_id.routing_id.location_id.id) or False,
                                                            'product_uos_qty': -line.product_uos_qty,
                                                            'product_uos': line.product_uos.id or False,
                                                            'production_id': production_id
                })

            bom_result = self.pool.get('mrp.production').action_compute(cr, uid,
                    [production_id], properties=[x.id for x in bom_id.property_ids if x])
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_confirm', cr)
        return {}

mrp_reversed_bom()


