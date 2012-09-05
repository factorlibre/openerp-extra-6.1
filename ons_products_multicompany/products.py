# -*- coding: utf-8 -*-
#
#  File: sales.py
#  Module: ons_advanced_multi_company
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
import tools
import netsvc
import time

class product_product(osv.osv):
	_inherit = "product.product"

	# The type, procure and supply methods of a product are no more stored in product_template,
	# instead, they are stored in ir_property, using this schema:
	#	create_uid and create_date as usual
	#	name = name of field: 
	#			'type'
	#			'supply_method'
	#			'procure_method'
	#	value_text = user's choice, instead of:
	#			product_template.type
	#			product_template.supply_method
	#			product_template.procure_method
	#	res_id = 'product.template,n' where n = record ID in product_template
	#	fields_id = ID 'type', 'supply_method' or 'procure_method' field in
	#			product_template, as found in ir_model_fields 
	#	type = 'relation'
	def get_contextual_values(self, cr, uid, ids, field_name, arg, context={}):
		result = {}
		usr = self.pool.get('res.users').browse( cr, uid, uid, context=context )
		props_obj = self.pool.get('ir.property')
		#logger = netsvc.Logger()
		
		for id in ids:
			result[id] = False
		s_ids = ','.join(map(lambda x: str(x), ids))
		query = "Select pp.id, pt.type From product_product pp, product_template pt where pp.product_tmpl_id=pt.id and pp.id in (" + s_ids + ")"
		cr.execute(query)
		rows = cr.fetchall() 
		if rows:
			for row in rows:
				if row[1]:
					result[ row[0] ] = row[1]
		#logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, " product::get_contextual_values( for field " + field_name + " ) - result="+str(result))

		field_id = self.pool.get('ir.model.fields').search( cr, uid, [('model','=','product.template'),('name','=',field_name)], context=context )[0]
		if usr and field_id:
			for id in ids:
				query = "Select pp.product_tmpl_id From product_product pp where pp.id=" + str(id)
				cr.execute(query)
				row = cr.fetchone()
				if row:
					prod_tmpl_id = row[0]
					filter = [('res_id','=', 'product.template,%d' % (prod_tmpl_id,)),('company_id','=',usr.company_id.id),('fields_id','=',field_id)]
					prop_ids = props_obj.search( cr, uid, filter, context=context )
					if prop_ids and len(prop_ids):
						row = props_obj.browse(cr, uid, prop_ids[0], context)
						if row:
							result[id] = row.value_text
		#logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, " product::get_contextual_values( ... ) - result="+str(result))
				
		return result

	_columns = {
		'type': fields.function( get_contextual_values, method=True, type='selection', selection=[
			('product','Stockable Product'),
			('consu', 'Consumable'),
			('service','Service')], string="Type", readonly=True ),
		'supply_method': fields.function(get_contextual_values, method=True, type='selection', selection=[
			('produce','Produce'),
			('buy','Buy')], string='Supply method', readonly=True ),
		'procure_method': fields.function(get_contextual_values, method=True, type='selection', selection=[
			('make_to_stock','Make to Stock'),
			('make_to_order','Make to Order')], string='Procure Method', readonly=True ),
	}
	
	def store_contextual_values(self, cr, uid, product_ids, field_name, vals, context={}):
		if field_name not in vals:
			return False

		usr = self.pool.get('res.users').browse( cr, uid, uid, context=context )
		props_obj = self.pool.get( 'ir.property' )
		field_id = self.pool.get( 'ir.model.fields' ).search( cr, uid, [('model','=','product.template'),('name','=',field_name)], context=context )[0]

		if isinstance(product_ids, (int, long)):
			product_ids = [product_ids]
		for product_id in product_ids:
			query = "Select pp.product_tmpl_id From product_product pp where pp.id=" + str(product_id)
			cr.execute(query)
			row = cr.fetchone()
			if row:
				prod_tmpl_id = row[0]
				filter = [('res_id','=', 'product.template,%d' % (prod_tmpl_id,)),('company_id','=',usr.company_id.id),('fields_id','=',field_id)]
				prop_ids = props_obj.search( cr, uid, filter, context=context )
				if prop_ids and len(prop_ids):
					prop_id = prop_ids[0]
					cr.execute("Update ir_property set value_text='"+vals[field_name]+"' Where id="+str(prop_id))
				else:
					cr.execute('SELECT nextval(%s)', ('ir_property_id_seq',))
					model_id = cr.fetchone()[0]
					query = "Insert into ir_property (id,create_uid,create_date,name,value_text,res_id,company_id,fields_id,type) Values ("
					query = query + str(model_id) + "," + str(uid) + ",'" + time.strftime('%Y-%m-%d %H:%M:%S') + "',"
					query = query + "'" + field_name + "','" + vals[field_name] + "','product.template," + str(prod_tmpl_id) + "'," + str(usr.company_id.id)
					query = query + "," + str(field_id) + ",'relation')"
					cr.execute(query)
		return True
	
	def create(self, cr, uid, vals, context={}):
		new_id = super(product_product, self).create(cr, uid, vals, context=context)
		if new_id:
			for field_name in [ 'type', 'supply_method', 'procure_method' ]:
				self.store_contextual_values(cr, uid, new_id, field_name, vals, context=context)

		return new_id

	def write(self, cr, uid, ids, vals, context=None):
		ret = super(product_product, self).write(cr, uid, ids, vals, context=context)
		for field_name in [ 'type', 'supply_method', 'procure_method' ]:
			self.store_contextual_values(cr, uid, ids, field_name, vals, context=context)

		return ret
		
	def unlink(self, cr, uid, ids, context=None):
		to_delete = []
		usr = self.pool.get('res.users').browse( cr, uid, uid, context=context )
		props_obj = self.pool.get( 'ir.property' )
		for field_name in [ 'type', 'supply_method', 'procure_method' ]:
			field_id = self.pool.get( 'ir.model.fields' ).search( cr, uid, [('model','=','product.template'),('name','=',field_name)], context=context )[0]
			if isinstance(ids, (int, long)):
				ids = [ids]
			#logger = netsvc.Logger()
			if ids:
				for id in ids:
					query = "Select pp.product_tmpl_id From product_product pp where pp.id=" + str(id)
					cr.execute(query)
					row = cr.fetchone()
					if row:
						prod_tmpl_id = row[0]
						filter = [('res_id','=', 'product.template,%d' % (prod_tmpl_id,)),('company_id','=',usr.company_id.id),('fields_id','=',field_id)]
						prop_ids = props_obj.search( cr, uid, filter, context=context )
						if prop_ids and len(prop_ids):
							prop_id = prop_ids[0]
							if prop_id:
								to_delete.append(prop_id)
	
			ret = super(product_product, self).unlink(cr, uid, ids, context=context)
			#logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, "To delete: "+str(to_delete))
			if ids:
				for prop_id in to_delete:
					logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, "Delete ID="+str(prop_id))
					cr.execute("Delete From ir_property Where id="+str(prop_id))
		return ret

product_product()
