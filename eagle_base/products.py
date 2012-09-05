# -*- coding: utf-8 -*-
#
#  File: products.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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

import netsvc
from osv import fields, osv

class product_recurrence_unit(osv.osv):
	_name = 'product.recurrence.unit'
	_description = "Recurrence units for the products and the warranties"
	_columns = {
		'name': fields.char('Name', size=64, required=True),
		'value': fields.integer('Value', required=True),
		'unit': fields.selection( [ ( 'day', 'Day' ), ( 'month', 'Month' ), ( 'year', 'Year' ) ], 'Units', required=True ),
	}

product_recurrence_unit()

class eagle_warranty( osv.osv ):
	_name = 'eagle.warranty'
	_description = 'Warranty'

	_columns = {
		'name': fields.char( 'Name', type='char', size=64, required=True ),
		'recurrence_id': fields.many2one( 'product.recurrence.unit', 'Recurrence' ),
	}

eagle_warranty()
	
class product_product( osv.osv ):
	_inherit = 'product.product'
	_columns = {
		'recurrence_id': fields.many2one( 'product.recurrence.unit', 'Recurrence' ),
		'warranty_id': fields.many2one( 'eagle.warranty', 'Warranty' ),
	}

product_product()
