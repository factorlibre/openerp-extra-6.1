# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_project
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

	_eagle_view_selection_account_visible = True
	_eagle_view_selection_mgt_visible = False
	_eagle_view_selection_crm_visible = False
	def get_view_selections(self, cr, uid, context={}):
		lst = super( eagle_contract, self ).get_view_selections( cr, uid, context=context )
		if self._eagle_view_selection_mgt_visible:
			lst += [('moves','Stock Moves')]
		if self._eagle_view_selection_crm_visible:
			lst += [('crm','CRM')]
		return lst

	def __init__(self, pool, cr):
		super( eagle_contract, self ).__init__(pool, cr)
		funcs = [ 
			('inst','do_contract_prj_installation'),
			]
		for func_item in funcs:
			self.register_event_function( cr, 'Eagle Projects', func_item[0], func_item[1] )

	def _get_analytic_account( self, cr, uid, ids, name, args, context ):
		res = {}
		for cnt in self.browse( cr, uid, ids, context=context ):
			res[cnt.id] = False
			if cnt.project_id and cnt.project_id.analytic_account_id:
				res[cnt.id] = cnt.project_id.analytic_account_id.id
		
		return res

	def _get_account_analytic_lines( self, cr, uid, cnt_ids, name, args, context ):
		res = {}
		projects = self.pool.get( 'project.project' )
		for cnt_id in cnt_ids:
			res[cnt_id] = []
			pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'grouping' )] )
			if pp_ids and len( pp_ids ) > 0:
				lst = []
				for project in projects.browse( cr, uid, pp_ids, context=context ):
					aaa = project.analytic_account_id
					if aaa:
						lst = lst + [x.id for x in aaa.line_ids]
				res[cnt_id] = lst
			pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'inst' )] )
			if pp_ids and len( pp_ids ) > 0:
				lst = []
				for project in projects.browse( cr, uid, pp_ids, context=context ):
					aaa = project.analytic_account_id
					if aaa:
						lst = lst + [x.id for x in aaa.line_ids]
				res[cnt_id] = res[cnt_id] + lst
			pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'maint' )] )
			if pp_ids and len( pp_ids ) > 0:
				lst = []
				for project in projects.browse( cr, uid, pp_ids, context=context ):
					aaa = project.analytic_account_id
					if aaa:
						lst = lst + [x.id for x in aaa.line_ids]
				res[cnt_id] = res[cnt_id] + lst
		
		return res
	
	def _store_account_analytic_lines(self, cr, uid, ids, field_name, field_value, arg, context):
		if field_name != 'account_analytic_lines' or not field_value:
			return False
		self.pool.get( 'account.analytic.line' ).write( cr, uid, field_value[0][1], field_value[0][2], context=context )
		return True

	def _get_cl_totals_prj( self, cr, uid, cnt_ids, name, args, context={} ):
		res = {}
		for cnt in self.browse( cr, uid, cnt_ids, context=context ):
			tots = { 'c_amount': 0.0, 'c_total': 0.0 }
			for cl in cnt.positions:
				tots['c_amount'] += cl.cl_amount
				tots['c_total'] += cl.cl_total
			tots['c_taxes'] = tots['c_total'] - tots['c_amount']
			res[cnt.id] = tots[ name ]
		
		return res
	
	_columns = {
		'project_id': fields.many2one( 'project.project', 'Project' ),
		'project_ids': fields.one2many( 'project.project', 'contract_id', 'Project and sub-projects' ),
		'tasks': fields.one2many( 'project.task', 'contract_id', string="Tasks",  domain=[('state','!=','done')] ),
		'works': fields.one2many( 'project.task.work', 'contract_id', 'Contracts works' ),
		'account_analytic_account': fields.function( _get_analytic_account, method=True, type='many2one', obj="account.analytic.account", string="Analytic Account" ),
		'account_analytic_lines': fields.function( _get_account_analytic_lines, fnct_inv=_store_account_analytic_lines, method=True, type='one2many', obj="account.analytic.line", string="Account Analytic Lines" ),
		'ons_hrtif_to_invoice': fields.many2one('hr_timesheet_invoice.factor', 'Reinvoice Costs', required=True, 
			help="Fill this field if you plan to automatically generate invoices based " \
			"on the costs in this analytic account: timesheets, expenses, ..." \
			"You can configure an automatic invoice rate on analytic accounts."),
		'c_amount': fields.function( _get_cl_totals_prj, method=True, type="float", string='Tax-free Amount', digits_compute=dp.get_precision('Sale Price') ),
		'c_taxes': fields.function( _get_cl_totals_prj, method=True, type="float", string='Taxes', digits_compute=dp.get_precision('Sale Price') ),
		'c_total': fields.function( _get_cl_totals_prj, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
		'view_selection': fields.selection( get_view_selections, 'View selection' ),
	}

	def _default_hrtif_id(self, cr, uid, context=None):
		cr.execute( "select id from hr_timesheet_invoice_factor order by factor asc limit 1" )
		row = cr.fetchone()
		ret = False
		if row and row[0]:
			ret = row[0]
		
		return ret

	_defaults = {
		'ons_hrtif_to_invoice': _default_hrtif_id,
	}

	def _setup_the_projects( self, cr, uid, ids, context={} ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "About to setup the projects for the contract id "+str(ids) )

		projects = self.pool.get( 'project.project' )
		aaa_obj = self.pool.get('account.analytic.account')
		tmp_ids = aaa_obj.search( cr, 1, [('code','=','3')], context=context )
		root_id = tmp_ids and len(tmp_ids) > 0 and tmp_ids[0] or False
		if isinstance( ids, (int, long) ):
			ids = [ids]
		for cnt in self.browse( cr, uid, ids, context=context ):
			if cnt.project_id:
				continue

			addr_id = False
			if cnt.customer_id:
				res = self.pool.get('res.partner').address_get(cr, uid, [cnt.customer_id.id], ['invoice'])
				addr_id = res['invoice']
			prj_vals = {
				'name': cnt.name,
				'sequence':1,
				'contract_id': cnt.id,
				'partner_id': cnt.customer_id and cnt.customer_id.id or False,
				'contact_id': addr_id,
				'project_use': 'grouping',
				'parent_id': root_id,
			}
			new_prj_id = projects.create( cr, uid, prj_vals, context=context )
			if not new_prj_id:
				continue

			# The contract keeps track of the parent project
			self.write( cr, uid, cnt.id, { 'project_id': new_prj_id } )
			
			# Retrieve the parent project itself to add it two children
			proj = projects.browse( cr, uid, new_prj_id, context=context )
			parent_acc_id = proj and proj.analytic_account_id and proj.analytic_account_id.id or False

			# Build a new sub-project for the installation process
			prj_vals = {
				'name': cnt.name + ' - ' + _( 'Installation' ),
				'sequence':2,
				'contract_id': cnt.id,
				'partner_id': cnt.customer_id and cnt.customer_id.id or False,
				'contact_id': addr_id,
				'project_use': 'inst',
			}
			p_id1 = projects.create( cr, uid, prj_vals )
			
			# Build a new sub-project for the maintenance process
			prj_vals = {
				'name': cnt.name + ' - ' + _( 'Maintenance' ),
				'sequence':3,
				'contract_id': cnt.id,
				'partner_id': cnt.customer_id and cnt.customer_id.id or False,
				'contact_id': addr_id,
				'project_use': 'maint',
			}
			p_id2 = projects.create( cr, uid, prj_vals, context=context )

			# Link the two new children to their common parent
			projects.write( cr, uid, [p_id1, p_id2], {'parent_id': parent_acc_id}, context=context )
		
		return True

	# Start the installation
	def do_contract_prj_installation( self, cr, uid, cnt_ids, context={} ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "do_contract_prj_installation() called" )
		if isinstance( cnt_ids, (int,long) ): cnt_ids = [cnt_ids]

		for cnt_id in cnt_ids:
			self._setup_the_projects( cr, uid, cnt_id, context=context )

		return True

eagle_contract()

class eagle_contract_pos( osv.osv ):
	_inherit = 'eagle.contract.position'

	def _amount_line_prj(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		if context is None:
			context = {}

		if field_name == 'cl_amount':
			for line in self.browse(cr, uid, ids, context=context):
				#price = line.list_price * (1 - (line.discount or 0.0) / 100.0)
				if line.is_billable:
					price = line.list_price
					res[line.id] = price * line.qty
				else:
					res[line.id] = 0.0
		else:
			tax_obj = self.pool.get('account.tax')
			cur_obj = self.pool.get('res.currency')
			for line in self.browse(cr, uid, ids, context=context):
				#price = line.list_price * (1 - (line.discount or 0.0) / 100.0)
				if line.is_billable:
					price = line.list_price
					taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.qty, None, line.name, line.contract_id.customer_id)
					cur = line.contract_id.pricelist_id and line.contract_id.pricelist_id.currency_id or False
				   	res[line.id] = cur and cur_obj.round(cr, uid, cur, taxes['total_included']) or taxes['total_included']
				   	if field_name == 'cl_taxes':
				   		res[line.id] = res[line.id] - price * line.qty
				else:
					res[line.id] = 0.0

		return res

	_columns = {
		'cl_amount': fields.function( _amount_line_prj, method=True, type="float", string='Tax-free Amount', digits_compute=dp.get_precision('Sale Price') ),
		'cl_taxes': fields.function( _amount_line_prj, method=True, type="float", string='Tax Amount', digits_compute=dp.get_precision('Sale Price') ),
		'cl_total': fields.function( _amount_line_prj, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
		'tax_id': fields.many2many('account.tax', 'eagle_contrat_line_tax', 'cnt_line_id', 'tax_id', 'Taxes'),
	}
	
	def recomp_line(self, cr, uid, ids, product, customer, qty, list_price, tax_id):
		if not product or not customer: return False

		tax_free = qty * list_price
		tax_obj = self.pool.get('account.tax')
		taxes = []
		if tax_id and isinstance(tax_id,list):
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "About to handle the taxes with tax_id="+str(tax_id) )
			if isinstance(tax_id[0],(list,tuple)) and len(tax_id[0]) == 3 and isinstance(tax_id[0][2], list):
				if len(tax_id[0][2]):
					taxes = tax_obj.browse(cr, uid,  tax_id[0][2])
			else:
				taxes = tax_obj.browse(cr, uid, tax_id )

		res = tax_obj.compute_all(cr, uid, taxes, list_price, qty, None, product, customer)
		
		return { 'value': {
			'cl_amount': tax_free,
			'cl_taxes': res['total_included'] - tax_free,
			'cl_total': res['total_included'],
		} }

	def onchange_product(self, cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id):
		if not product_id:
			return { 'value': {} }
		res = super( eagle_contract_pos, self ).onchange_product( cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id )
		if not qty or qty == 0.0:
			qty = res['value']['qty']

		fpos = False		# for now, as of 24 june 2011, fiscal position is ignored
		prod = self.pool.get('product.product').browse(cr, uid, product_id)
		res['value']['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, prod.taxes_id)
		if 'list_price' in res['value']:
			res['value'].update( { 'cl_amount': qty * res['value']['list_price'] } )
			vals = self.recomp_line( cr, uid, [], product_id, partner_id, qty, res['value']['list_price'], res['value']['tax_id'] )
			res['value'].update( { 'cl_total': vals['value']['cl_total'] } )

		prod = self.pool.get('product.product').browse(cr, uid, product_id)
		delay = prod.sale_delay or False
		if prod.type == 'product':
			if prod.supply_method == 'buy':
				delay = prod.sale_delay
				if prod.seller_ids and len(prod.seller_ids) > 0:
					suppl = prod.seller_ids[0]
					delay = suppl.delay
			else:	# prod.supply_method == 'produce'
				delay = prod.produce_delay
		elif prod.type == 'service':
			uom = prod.uom_id
			q = 1.0
			if uom and uom.factor_inv != 0.0:
				q = uom.factor_inv
			delay = qty * q
		res['value'].update( { 'product_duration': delay } )

		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "Eagle Project's onchange_product() is returning: "+str(res) )

		return res

eagle_contract_pos()

