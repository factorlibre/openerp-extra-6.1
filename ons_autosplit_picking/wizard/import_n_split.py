# -*- coding: utf-8 -*-
#
#  File: wizard/import_n_split.py
#  Module: ons_autosplit_picking
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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

from osv import osv, fields
import netsvc
import base64
import tools
from tools.translate import _
import csv

class import_n_split(osv.osv_memory):
	"""Import and split a picking's details"""
	
	_name = 'ons.import_n_split'
	_description = 'Import and split the details of a picking'
	columns_to_fields = {
		'prodlot': 'prodlot_id',
		'tracking': 'tracking_id',
	}

	_columns = {
		'csv_file': fields.binary('Select an CSV File', filters='*.csv', required=True),
	}
	
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', 
						context=None, toolbar=False, submenu=False):
		""" Changes the view dynamically
		 @param self: The object pointer.
		 @param cr: A database cursor
		 @param uid: ID of the user currently logged in
		 @param context: A standard dictionary 
		 @return: New arch of view.
		"""
		res = super(import_n_split, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
		record_id = context and context.get('active_id', False) or False
		assert record_id,'Active ID not found'
		pick_obj = self.pool.get('stock.picking')
		pick = pick_obj.browse(cr, uid, record_id, context=context)

		# Forget if there's not exactely one stock move
		if len(pick.move_lines) != 1:
			res['fields'] = {}
			res['arch'] = """<form string="File to import">
            <label string="%s" colspan="4"/>
            <separator string="" colspan="4"/>
			<group col="4" colspan="4">
                        <button special="cancel" string="Cancel" icon="gtk-cancel"/>
            </group>
            </form>""" % _('You can use this wizard on pickings with one and only one move.')

		return res

	def do_it(self, cr, uid, ids, context=None):
		"""
		This function .
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of IDs
		@param context: A standard dictionary for contextual values
		
		@return : an empty dictionary.
		"""
		
		# Here is an example of could be in csv_content
		# 	"Qty","prodlot","tracking"
		# 	1,"CNSTP08207030","085511020291554209"
		# 	1,"CNSTP08207030","085511021411014209"
		# 	1,"CNSTP08207030","085511021431334209"
		# 	1,"CNSTP08207030","085511022150614209"
		# 	1,"CNSTP08207030","085511022160244209"
		# 	1,"CNSTP08207031","085511022160804209"
		# 	1,"CNSTP08207031","085511110101200210"
		# 	1,"CNSTP08207031","085511110120020210"
		# 	1,"CNSTP08207031","085511110120740210"
		# 	1,"CNSTP08207031","085511110130070210"
		# 	1,"CNSTP08207031","085511110160080210"
		# 	1,"CNSTP08207031","085511110300360210"

		if not context:
			context = {}
		
		for id in ids:
			obj = self.browse(cr, uid, id, context=context)
			csv_content = base64.decodestring(obj.csv_file).split('\n')

			# This will facilitate the decoding of the CSV content
			lines = csv.reader(csv_content, delimiter=',')
			fields = lines.next()
			
			# Here we clean somewhat the list of lines so that we have an idea of how many lines there are
			i = 0
			while(i < len(csv_content)):
				if len(csv_content[i].strip()) < 1:
					del csv_content[i]
				else:
					i += 1
			csv_count = len(csv_content) - 1

			move_obj = self.pool.get('stock.move')
			pick_obj = self.pool.get('stock.picking')
			prodlot_obj = self.pool.get('stock.production.lot')
			tracking_obj = self.pool.get('stock.tracking')

			record_id = context and context.get('active_id', False) or False
			assert record_id,'Active ID not found'
			pick = pick_obj.browse(cr, uid, record_id, context=context)
			if len(pick.move_lines) != 1:
				continue
			count = 0
			for move in pick.move_lines:
				if move.product_qty != csv_count:
					msg = _('The quantity (%d) does not correspond to the number of lines (%d) of the CSV file.' ) % ( move.product_qty, csv_count )
					raise osv.except_osv( 'Error!', msg )
				
				# In the future, it may be replaced by one of the CSV's column
				new_qty = 1.0
				new_uos_qty = new_qty / move.product_qty * move.product_uos_qty
				
				# loop through the CSV lines
				tracking_id = False
				prodlot_id = False
				for line in lines:
					vals = {}
					# Setup the columns and their values
					for col in self.columns_to_fields.keys():
						if col not in fields:
							continue
						val = line[ fields.index(col) ]
						if col == 'prodlot':
							prodlot_vals = {
								'ref': val,
								'product_id': move.product_id.id, 
							}
							prodlot_ids = prodlot_obj.search(cr, uid, [('ref','=',val)], context=context)
							if not prodlot_ids or len(prodlot_ids) < 1:
								prodlot_id = prodlot_obj.create(cr, uid, prodlot_vals, context=context)
							else:
								prodlot_id = prodlot_ids[0]
							if prodlot_id:
								vals[self.columns_to_fields[col]] = prodlot_id
						elif col == 'tracking':
							tracking_vals = {
								'serial': val, 
							}
							tracking_ids = tracking_obj.search(cr, uid, [('serial','=',val)], context=context)
							if not tracking_ids or len(tracking_ids) < 1:
								tracking_id = tracking_obj.create(cr, uid, tracking_vals, context=context)
							else:
								tracking_id = tracking_ids[0]
							if tracking_id:
								vals[self.columns_to_fields[col]] = tracking_id
						elif hasattr(move,self.columns_to_fields[col]):
							vals[self.columns_to_fields[col]] = val
					if prodlot_id and tracking_id:
						tracking_obj.write(cr, uid, [tracking_id], {'prodlot_id':prodlot_id}, context=context)
					vals.update({'product_qty' : new_qty, 'product_uos_qty': new_uos_qty, 'state':move.state})

					if count == 0:
						move_obj.write(cr, uid, move.id, vals, context=context)
					else:
						new_obj = move_obj.copy(cr, uid, move.id, vals)
					count += 1
	
		return {'type': 'ir.actions.act_window_close'}

import_n_split()
