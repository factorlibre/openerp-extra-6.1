# -*- coding: utf-8 -*-
#
#  File: wizard/wiz_setup_product_type.py
#  Module: ons_advanced_multi_company
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

from osv import osv, fields
from tools.translate import _
import time
import netsvc

class wiz_setup_product_type(osv.osv_memory):
	_name = 'ons.product.ctx.vals'
	_description = 'Change the contextual values of a product'

	def _get_prod_tmpl_type(self, cr, uid, context={}):
		ret = 'product'
		obj_pp = self.pool.get('product.product')
		if context is None:
			context = {}
		if context.get('active_id',False):
			ret = obj_pp.browse(cr, uid, context['active_id']).type
		
		return ret

	def _get_prod_tmpl_supply_method(self, cr, uid, context={}):
		ret = 'product'
		obj_pp = self.pool.get('product.product')
		if context is None:
			context = {}
		if context.get('active_id',False):
			ret = obj_pp.browse(cr, uid, context['active_id']).supply_method
		
		return ret

	def _get_prod_tmpl_procure_method(self, cr, uid, context={}):
		ret = 'product'
		obj_pp = self.pool.get('product.product')
		if context is None:
			context = {}
		if context.get('active_id',False):
			ret = obj_pp.browse(cr, uid, context['active_id']).procure_method
		
		return ret

	_columns = {
		'prod_type': fields.selection([('product','Stockable Product'),('consu', 'Consumable'),('service','Service')], 'Product Type', required=True),
		'prod_supply_method': fields.selection([('produce','Produce'),('buy','Buy')], 'Supply method', required=True),
		'prod_procure_method': fields.selection([('make_to_stock','Make to Stock'), ('make_to_order','Make to Order')], 'Procure Method', required=True),
	}
	
	_defaults = {
		'prod_type': _get_prod_tmpl_type,
		'prod_supply_method': _get_prod_tmpl_supply_method,
		'prod_procure_method': _get_prod_tmpl_procure_method
	}
	
	def store_contextual_values(self, cr, uid, ids, context=None):
		if not context.get('active_id',False):
			return False

		data = self.read(cr, uid, ids)[0]
		prod_id = context['active_id']
		for field_name in [ 'type', 'supply_method', 'procure_method' ]:
			vals = { field_name: data[ 'prod_' + field_name ] }
			producs = self.pool.get('product.product').store_contextual_values( cr, uid, prod_id, field_name, vals, context=context )
			
		return {}

	def change_prod_type(self, cr, uid, ids, context=None):
		if not context.get('active_id',False):
			return False
		data = self.read(cr, uid, ids)[0]
		new_type = data['prod_type']
		logger = netsvc.Logger()

		prod_id = context['active_id']
		usr = self.pool.get('res.users').browse( cr, uid, uid, context=context )
		props_obj = self.pool.get( 'ir.property' )
		field_id = self.pool.get( 'ir.model.fields' ).search( cr, uid, [('model','=','product.template'),('name','=','type')], context=context )[0]
		query = "Select pp.product_tmpl_id From product_product pp where pp.id=" + str(prod_id)
		cr.execute(query)
		row = cr.fetchone()
		if not row:
			return False
		prod_tmpl_id = row[0]
		filter = [('res_id','=', 'product.template,%d' % (prod_tmpl_id,)),('company_id','=',usr.company_id.id),('fields_id','=',field_id)]
		prop_ids = props_obj.search( cr, uid, filter, context=context )
		if prop_ids and len(prop_ids):
			logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, "Updating with prod_tmpl_id="+str(prod_tmpl_id)+" and type="+new_type)
			cr.execute("Update ir_property set value_text='"+new_type+"' Where id="+str(prop_ids[0]))
		else:
			cr.execute('SELECT nextval(%s)', ('ir_property_id_seq',))
			model_id = cr.fetchone()[0]
			query = "Insert into ir_property (id,create_uid,create_date,name,value_text,res_id,company_id,fields_id,type) Values ("
			query = query + str(model_id) + "," + str(uid) + ",'" + time.strftime('%Y-%m-%d %H:%M:%S') + "',"
			query = query + "'type','" + new_type + "','product.template," + str(prod_tmpl_id) + "'," + str(usr.company_id.id)
			query = query + "," + str(field_id) + ",'relation')"
			logger.notifyChannel("Cyp:debug", netsvc.LOG_DEBUG, "Insert query: "+query)
			cr.execute(query)
			
		return {}

wiz_setup_product_type()
