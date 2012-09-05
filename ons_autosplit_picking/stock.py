# -*- coding: utf-8 -*-
#
#  File: stock.py
#  Module: ons_autosplit_picking
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
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

class stock_tracking(osv.osv):
	_inherit = "stock.tracking"
	
	_columns = {
		'prodlot_id': fields.many2one('stock.production.lot', 'Production lot', select=True),
	}

stock_tracking()

class stock_production_lot(osv.osv):
	_inherit = 'stock.production.lot'
	_columns = {
		'tracking_ids': fields.one2many('stock.tracking', 'prodlot_id', 'Trackings for this production lot', readonly=True),
	}

stock_production_lot()
