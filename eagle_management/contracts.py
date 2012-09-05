# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_management
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

import netsvc
from osv import fields, osv
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tools
from tools.translate import _
import decimal_precision as dp

class eagle_contract( osv.osv ):
	_inherit = 'eagle.contract'
	_eagle_view_selection_mgt_visible = True

	def __init__(self, pool, cr):
		super( eagle_contract, self ).__init__(pool, cr)
		funcs = [ 
			('inst','do_contract_mgt_installation'),
			]
		for func_item in funcs:
			self.register_event_function( cr, 'Eagle Management', func_item[0], func_item[1] )
			
	def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if field_name == 'eagle_make_sale_button_visible':
			val = True
			if eagle_param:
				if eagle_param.selling_mode == 'disabled':
					val = False
				
			for pos_id in pos_ids:
				res[pos_id] = val

		return res

	def get_active_tabs(self, cr, uid, cnt_ids, field_name, args, context={}):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		tabs = False
		if eagle_param:
			if not eagle_param.show_all_meta_tabs:
				if eagle_param.tabs:
					tabs = eagle_param.tabs.split(';')
				user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
				if user and user.eagle_tabs:
					tabs = user.eagle_tabs.split(';')
		if not tabs:
			tabs = []
			for item in self.get_view_selections(cr, uid, context=context):
				tabs.append(item[0])
		tab_name = field_name.split('_')[1]
		val = tab_name in tabs

		for cnt_id in cnt_ids:
			res[cnt_id] = val
			
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "get_active_tabs() called with field_name="+str(field_name)+", returning: "+str(res))
		
		return res

	_columns = {
		'current_sale_order_lines': fields.one2many( 'sale.order.line', 'contract_id', 'Current Sale Order Lines', domain=[('state','=','draft')] ),
		'past_sale_order_lines': fields.one2many( 'sale.order.line', 'contract_id', 'Past Sale Order Lines', domain=[('state','<>','draft')] ),
		'account_invoices': fields.one2many( 'account.invoice', 'contract_id', 'Invoices' ),
		'stock_moves': fields.one2many( 'stock.move', 'contract_id', 'Moves' ),
		'purchase_orders': fields.one2many( 'purchase.order', 'contract_id', string="Purchases" ),
		'stock_pickings_in': fields.one2many( 'stock.picking', 'contract_id', 'Incoming products', domain=[('type','=','in')] ),
		'stock_pickings_out': fields.one2many( 'stock.picking', 'contract_id', 'Outgoing products', domain=[('type','=','out')] ),
		'procurement_orders': fields.one2many( 'procurement.order', 'contract_id', string="Procurements" ),
		'eagle_make_sale_button_visible': fields.function( _eagle_params, method=True, type='boolean', string="'Make Sale' Button visible?" ),
		'activeTab_moves': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: moves" ),
	}

	def _make_the_sales( self, cr, uid, ids, context={}, handle_financial_partner=False, exception_allowed=False ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "_make_the_sales() called" )

		sales = self.pool.get( 'sale.order' )
		sale_lines = self.pool.get( 'sale.order.line' )
		contracts_lines = self.pool.get( 'eagle.contract.position' )
		recurrences = self.pool.get( 'product.recurrence.unit' )
		projects = self.pool.get( 'project.project' )

		cr.execute( "select s.id from sale_shop s, stock_warehouse w, res_users u where s.warehouse_id=w.id and w.company_id=u.company_id and u.id=" + str( uid ) )
		row = cr.fetchone()
		if not row or len( row ) < 1:
			if exception_allowed:
				raise osv.except_osv(_('Error !'), _('No Sale Shop found with the current user!\nPlease define one.'))
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "No Sale Shop found with the current user... please select one" )
			return False
		shop_id = row[0]

		if isinstance( ids, (int, long) ):
			ids = [ids]

		for contract in self.browse( cr, uid, ids, context=context ):
			if contract.state not in ['installation','production']:
				continue
			
			# Loop through the sale order line and add the products while needed:
			#	- recurrents objects are added if the current date is after the cancellation deadline 
			#		and before the next invoice date
			#	- for non-recurrents objects:
			#		- those in 'open' state are added
			#		- the others are skipped
			#	- each time a contract line is copied into a sale order line, its state is set to 'done'
			#	- if a financial partner is defined, then the non-recurrent products are put in a separated
			#	  SO with the financial partner defined
			#	  Else:
			#		- non-recurrent products are put in a sale order
			#		- recurrent products may be put either in the same or in a different SO, depending on
			#		  how much time has passed between 1st SO and 1st occurence of the recurrent products
			so_id = False
			so = False
			fp = False
			for cnt_line in contract.positions:
				if cnt_line.state != 'open':
					continue

				if cnt_line.next_invoice_date:
					now = datetime.now()
					next = datetime.strptime( cnt_line.next_invoice_date, '%Y-%m-%d' )
					if now < next:
						continue

				if not so_id:
					if not handle_financial_partner:
						so_ids = sales.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ] )
						if so_ids and len( so_ids ) > 0:
							for so in sales.browse( cr, uid, so_ids, context=context ):
								if so.financial_partner_id:
									so_id = so.id
									break
							if not so_id:
								so_id = so_ids[len(so_ids)-1]
					if not so_id:
						vals = {
							'name': self.pool.get( 'ir.sequence' ).get( cr, uid, 'sale.order' ) + '/' + contract.name,
							'date_order': datetime.now().strftime( '%Y-%m-%d' ),
							'shop_id': shop_id,
							'partner_id': contract.customer_id.id,
							'financial_partner_id': contract.financial_partner_id and contract.financial_partner_id.id or False,
							'user_id': uid,
							'contract_id': contract.id,
						}
						part = sales.onchange_partner_id( cr, uid, ids, contract.customer_id.id )
						vals.update( part['value'] )
						if contract.pricelist_id:
							vals['pricelist_id'] = contract.pricelist_id.id
						so_id = sales.create( cr, uid, vals, context=context )
						if so_id and hasattr(contract, 'project_id'):
							if contract.project_id:
								proj_use = contract.state == 'installation' and 'inst' or 'maint'
								proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id),('project_use','=',proj_use)], context=context )
								if not proj_ids or not len( proj_ids ):
									proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id)], context=context )
								if proj_ids and len( proj_ids ):
									proj = projects.browse( cr, uid, proj_ids[0], context=context )
									if proj and proj.analytic_account_id:
										sales.write( cr, uid, [so_id], {'project_id':proj.analytic_account_id.id} )
				if not so_id:
					break
				if not so:
					so = sales.browse( cr, uid, so_id, context=context )
					if not so:
						so_id = False
						break
					fp = so.fiscal_position and so.fiscal_position.id or False
				
				now = datetime.now().strftime( '%Y-%m-%d' )
				if not cnt_line.next_invoice_date or cnt_line.next_invoice_date == now:
					tmp = sale_lines.product_id_change( cr, uid, ids, so.pricelist_id.id, int( cnt_line.name ), 
							qty=cnt_line.qty, partner_id=so.partner_id.id, date_order=so.date_order, fiscal_position=fp )
					vals = tmp['value']
					vals['order_id'] = so_id
					vals['contract_id'] = contract.id
					vals['salesman_id'] = uid
					vals['product_id'] = int( cnt_line.name )
					vals['product_uom_qty'] = cnt_line.qty
					vals['product_uos_qty'] = cnt_line.qty
					vals['contract_pos_id'] = cnt_line.id
					vals['price_unit'] = cnt_line.list_price
					vals['notes'] = cnt_line.notes
					vals['tax_id'] = [(6,0, [x.id for x in cnt_line.tax_id])]
					if cnt_line.out_description and cnt_line.out_description != '':
						vals['name'] = cnt_line.out_description
					if not cnt_line.is_billable:
						vals['discount'] = 100.0
					netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "About to create a Sol with vals="+str(vals))
					sol_id = sale_lines.create( cr, uid, vals, context=context )
					if sol_id:
						contracts_lines.write( cr, uid, cnt_line.id, { 'state': 'done' }, context=context )

			if handle_financial_partner:
				so_id = False
				so = False
		
			if contract.state == 'production':

				for cnt_line in contract.positions:
					if not cnt_line.is_active: continue
					if cnt_line.state != 'recurrent': continue
					if not cnt_line.recurrence_id: continue
					if not cnt_line.next_invoice_date: continue
	
					recurrence = recurrences.browse( cr, uid, cnt_line.recurrence_id.id )
					if not recurrence:
						continue
	
					now = datetime.now().strftime( '%Y-%m-%d' )
					next = datetime.strptime( cnt_line.next_invoice_date, '%Y-%m-%d' )
					dt = next - relativedelta( days=cnt_line.cancellation_deadline )
					before = dt.strftime( '%Y-%m-%d' )
					if recurrence.unit == 'day':
						after = next + relativedelta( days=recurrence.value )
						if recurrence.value > 0:
							after -= relativedelta( days=1 )
					elif recurrence.unit == 'month':
						after = next + relativedelta( months=recurrence.value )
						if recurrence.value > 0:
							after -= relativedelta( days=1 )
					elif recurrence.unit == 'year':
						after = next + relativedelta( years=recurrence.value )
						if recurrence.value > 0:
							after -= relativedelta( days=1 )
					if before > now:
						continue
					
					if not so_id:
						so_ids = sales.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ] )
						if so_ids and len( so_ids ) > 0:
							for so in sales.browse( cr, uid, so_ids, context=context ):
								if not so.financial_partner_id:
									so_id = so.id
									break
						if not so_id:
							vals = {
								'name': self.pool.get( 'ir.sequence' ).get( cr, uid, 'sale.order' ) + '/' + contract.name,
								'date_order': datetime.now().strftime( '%Y-%m-%d' ),
								'shop_id': shop_id,
								'partner_id': contract.customer_id.id,
								'financial_partner_id': False,
								'user_id': uid,
								'contract_id': contract.id,
							}
							part = sales.onchange_partner_id( cr, uid, ids, contract.customer_id.id )
							vals.update( part['value'] )
							if contract.pricelist_id:
								vals['pricelist_id'] = contract.pricelist_id.id
							so_id = sales.create( cr, uid, vals, context=context )
							if so_id and hasattr(contract, 'project_id'):
								if contract.project_id:
									# 2011-01-11/Cyp: Jae asked to put recurrrent tasks in 'Maintenance' project
									#proj_use = contract.state == 'installation' and 'inst' or 'maint'
									proj_use = 'maint'
									proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id),('project_use','=',proj_use)], context=context )
									if not proj_ids or not len( proj_ids ):
										proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id)], context=context )
									if proj_ids and len( proj_ids ):
										proj = projects.browse( cr, uid, proj_ids[0], context=context )
										if proj and proj.analytic_account_id:
											sales.write( cr, uid, [so_id], {'project_id':proj.analytic_account_id.id} )
							so = False
						if not so_id:
							break
					if so_id and not so:
						so = sales.browse( cr, uid, so_id, context=context )
					if not so:
						so_id = False
						break

					fp = so.fiscal_position and so.fiscal_position.id or False
					tmp = sale_lines.product_id_change( cr, uid, ids, so.pricelist_id.id, int( cnt_line.name ), 
							qty=cnt_line.qty, partner_id=so.partner_id.id, date_order=so.date_order, fiscal_position=fp )
					vals = tmp['value']
					vals['order_id'] = so_id
					vals['contract_id'] = contract.id
					vals['salesman_id'] = uid
					vals['product_id'] = int( cnt_line.name )
					vals['product_uom_qty'] = cnt_line.qty
					vals['product_uos_qty'] = cnt_line.qty
					vals['contract_pos_id'] = cnt_line.id
					vals['price_unit'] = cnt_line.list_price
					vals['notes'] = cnt_line.notes
					vals['tax_id'] = [(6,0, [x.id for x in cnt_line.tax_id])]
					txt = cnt_line.description + ' - ' + next.strftime( '%d.%m.%Y' ) + ' ' + _( 'to' ) + ' ' + after.strftime( '%d.%m.%Y' )
					vals['name'] = txt
					sol_id = sale_lines.create( cr, uid, vals, context=context )
					if sol_id:
						contracts_lines.write( cr, uid, cnt_line.id, { 'next_invoice_date': after.strftime( '%Y-%m-%d' ), 'out_description': txt }, context=context )

			eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
			if eagle_param and eagle_param.auto_production_state:
				valid = True
				for cnt_line in contract.positions:
					if cnt_line.state == 'open':
						valid = False
						break
				if valid:
					self.contract_production( cr, uid, [contract.id], {} )


	# Start the installation
	def do_contract_mgt_installation( self, cr, uid, cnt_ids, context={}, force_sale=False ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "do_contract_mgt_installation() called" )

		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )		
		if not eagle_param:
			return False
		if eagle_param.selling_mode != 'auto' and not force_sale:
			return False

		for cnt_id in cnt_ids:
			hfp = False
			cnt = self.browse( cr, uid, cnt_id, context=context )
			if cnt and cnt.financial_partner_id:
				hfp = True
			self._make_the_sales( cr, uid, cnt_id, context=context, handle_financial_partner=hfp, exception_allowed=True )

		return True

	# Activate the "Accounting" tabs
	def button_view_moves(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'view_selection':'moves'} )
		return True

	def button_make_sale(self, cr, uid, ids, context={}):
		return self.do_contract_mgt_installation( cr, uid, ids, context=context, force_sale=True )

	def run_mgt_scheduler( self, cr, uid, context={} ):
		''' Runs Management scheduler.
		'''
		if not context:
			context={}
		
		self_name = 'Eagle Management Scheduler'
		for contract in self.browse( cr, uid, self.search( cr, uid, [], context=context ), context=context ):
			if contract.state in ['installation','production']:
				netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "Checking contract '%s'" % contract.name )
				self.do_contract_mgt_installation( cr, uid, [contract.id], context=context )
		
		return True
		
eagle_contract()

class eagle_contract_pos(osv.osv):
	_inherit = 'eagle.contract.position'

	def _comp_start_date(self, cr, uid, pos_ids, field_name, arg, context=None):
		res = {}
		for pos_id in pos_ids:
			res[pos_id] = False
			pos = self.browse( cr, uid, pos_id, context=context)
			if pos and pos.stock_disposal_date:
				ds = datetime.strptime(pos.stock_disposal_date, '%Y-%m-%d')
				res[pos_id] = (ds + relativedelta(days=-pos.product_duration)).strftime('%Y-%m-%d')
		return res

	_columns = {
		'cust_delivery_date': fields.date('Customer Delivery Date'),
		'stock_disposal_date': fields.date('Stock Disposal Date'),
		'product_duration': fields.integer('Duration'),
		'cl_start_date': fields.function( _comp_start_date, method=True, type='date', string='Start date' ),
	}

	_defaults = {
	}

	def recomp_start_date(self, cr, uid, ids, disposal_date, duration):
		res = {}
		if disposal_date:
			ds = datetime.strptime(disposal_date, '%Y-%m-%d')
			res['cl_start_date'] = (ds + relativedelta(days=-duration)).strftime('%Y-%m-%d')
		return { 'value': res }
	

eagle_contract_pos()
