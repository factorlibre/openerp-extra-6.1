# -*- coding: utf-8 -*-
#
#  File: purchases.py
#  Module: eagle_contracts
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

from osv import fields, osv
import netsvc

class purchase_order( osv.osv ):
	_inherit = 'purchase.order'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def action_picking_create(self,cr, uid, ids, *args):
		picking_id = False
		for order in self.browse(cr, uid, ids):
			loc_id = order.partner_id.property_stock_supplier.id
			istate = 'none'
			if order.invoice_method=='picking':
				istate = '2binvoiced'
			pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
			picking_id = self.pool.get('stock.picking').create(cr, uid, {
				'name': pick_name,
				'origin': order.name+((order.origin and (':'+order.origin)) or ''),
				'type': 'in',
				'address_id': order.dest_address_id.id or order.partner_address_id.id,
				'invoice_state': istate,
				'purchase_id': order.id,
				'company_id': order.company_id.id,
				'move_lines' : [],
				'contract_id': order.contract_id and order.contract_id.id or False,
			})
			todo_moves = []
			for order_line in order.order_line:
				if not order_line.product_id:
					continue
				if order_line.product_id.product_tmpl_id.type in ('product', 'consu'):
					dest = order.location_id.id
					move = self.pool.get('stock.move').create(cr, uid, {
						'name': order.name + ': ' +(order_line.name or ''),
						'product_id': order_line.product_id.id,
						'product_qty': order_line.product_qty,
						'product_uos_qty': order_line.product_qty,
						'product_uom': order_line.product_uom.id,
						'product_uos': order_line.product_uom.id,
						'date': order_line.date_planned,
						'date_expected': order_line.date_planned,
						'location_id': loc_id,
						'location_dest_id': dest,
						'picking_id': picking_id,
						'move_dest_id': order_line.move_dest_id.id,
						'state': 'draft',
						'purchase_line_id': order_line.id,
						'company_id': order.company_id.id,
						'price_unit': order_line.price_unit,
						'contract_id': order.contract_id and order.contract_id.id or False,
					})
					if order_line.move_dest_id:
						self.pool.get('stock.move').write(cr, uid, [order_line.move_dest_id.id], {'location_id':order.location_id.id})
					todo_moves.append(move)
			self.pool.get('stock.move').action_confirm(cr, uid, todo_moves)
			self.pool.get('stock.move').force_assign(cr, uid, todo_moves)
			wf_service = netsvc.LocalService("workflow")
			wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
		return picking_id

purchase_order()

