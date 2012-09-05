# -*- coding: utf-8 -*-
#
#  File: stock.py
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

import netsvc
from osv import fields, osv

class stock_move( osv.osv ):
	_inherit = 'stock.move'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def create( self, cr, uid, vals, context=None ):
		if 'sale_line_id' in vals:
			sl_id = vals['sale_line_id']
			if sl_id:
				sol = self.pool.get( 'sale.order.line' ).browse( cr, uid, sl_id, context=context )
				if sol and sol.order_id and sol.order_id.contract_id:
					vals['contract_id'] = sol.order_id.contract_id.id
		return super( stock_move, self ).create( cr, uid, vals, context=context )

stock_move()

class stock_picking( osv.osv ):
	_inherit = 'stock.picking'

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}

	def create( self, cr, uid, vals, context=None ):
		sales = self.pool.get( 'sale.order' )
		if 'sale_id' in vals and vals['sale_id']:
			sale = sales.browse( cr, uid, vals['sale_id'], context=context )
			if sale and sale.contract_id:
				vals['contract_id'] = sale.contract_id.id
		return super( stock_picking, self ).create( cr, uid, vals, context=context )

stock_picking()
