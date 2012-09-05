# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_invoice
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
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from tools.translate import _

class eagle_contract( osv.osv ):
	_inherit = 'eagle.contract'
	_eagle_view_selection_account_visible = True

	def __init__(self, pool, cr):
		super( eagle_contract, self ).__init__(pool, cr)
		self.register_event_function( cr, 'Eagle Finances', 'inst', 'do_contract_inv_installation' )

	def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if field_name == 'eagle_make_invoice_button_visible':
			val = True
			if eagle_param:
				if eagle_param.invoicing_mode == 'disabled':
					val = False
				
			for pos_id in pos_ids:
				res[pos_id] = val

		return res

	_columns = {
		'current_invoice_lines': fields.one2many( 'account.invoice.line', 'contract_id', 'Current invoice lines', domain=[('invoice_id.state','=','draft')] ),
		'past_invoice_lines': fields.one2many( 'account.invoice.line', 'contract_id', 'Past invoice lines', domain=[('invoice_id.state','<>','draft')] ),
		'eagle_make_invoice_button_visible': fields.function( _eagle_params, method=True, type='boolean', string="'Make Invoice' Button visible?" ),
	}
	
	def get_invoice_default_values( self, cr, uid, contract, context={} ):
		invoice_obj = self.pool.get( 'account.invoice' )
		journal_obj = self.pool.get('account.journal')
		vals = {
			'name': contract.name,
			'origin': contract.name,
			'type': 'out_invoice',
			'state':'draft',
			'date_invoice': datetime.now().strftime( '%Y-%m-%d' ),
			'partner_id': contract.customer_id and contract.customer_id.id or False,
			'contract_id': contract.id,
		}
		
		res = journal_obj.search( cr, uid, [('type', '=', 'sale'), 
			('company_id', '=', contract.user_id.company_id.id),
			('refund_journal', '=', False)], context=context, limit=1 )
		journal_id = res and res[0] or False
		res = invoice_obj.onchange_journal_id( cr, uid, [], journal_id=journal_id )
		if res and res.get('value', False):
			vals['currency_id'] = res['value']['currency_id']
		vals['journal_id'] = journal_id
		
		res = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice', vals['partner_id'],\
			date_invoice=vals['date_invoice'], company_id=contract.user_id.company_id.id)
		vals.update( res['value'] )
		
		return vals
	
	def get_invoice_line_default_values( self, cr, uid, invoice, contract, contract_position, context={} ):
		invoice_lines = self.pool.get( 'account.invoice.line' )
		product_id = int( contract_position.name )
		product = self.pool.get( 'product.product' ).browse( cr, uid, product_id, context=context )
		vals = {
			'name': contract.name,
			'origin': contract.name,
			'invoice_id': invoice.id,
			'product_id': product_id,
			'contract_id': contract.id,
			'note': contract_position and contract_position.notes or False,
		}
		res = invoice_lines.product_id_change(cr, uid, [], product.id, product.uom_id and product.uom_id.id or False,  
			qty=contract_position.qty, name=product.name, type='out_invoice', 
			partner_id=contract.customer_id and contract.customer_id.id or False,
			address_invoice_id=invoice.address_invoice_id, currency_id=invoice.currency_id, context=context)
		vals.update( res['value'] )
		if 'invoice_line_tax_id' in vals:
			vals['invoice_line_tax_id'] = [(6, 0, vals['invoice_line_tax_id'])]
		if contract_position:
			vals.update( {'price_unit': contract_position.list_price,'quantity':contract_position.qty} )
			if not contract_position.is_billable:
				vals.update( {'discount':100.0} )
		
		return vals

	def do_contract_inv_installation( self, cr, uid, ids, context={}, force_invoicing=False ):
		invoices = self.pool.get( 'account.invoice' )
		invoice_lines = self.pool.get( 'account.invoice.line' )
		recurrences = self.pool.get( 'product.recurrence.unit' )
		contract_positions = self.pool.get( 'eagle.contract.position' )
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		
		if not eagle_param:
			return False
		if eagle_param.invoicing_mode != 'auto' and not force_invoicing:
			return False

		for contract in self.browse( cr, uid, ids, context=context ):
			if contract.state not in ['installation','production']:
				continue
			
			# This loop handles non-recurrent contract positions 
			#	- those in 'open' state are added
			#	- the others are skipped
			#	- each time an object is correctly added to an invoice, its state is set to 'done'
			invoice_id = False
			invoice = False
			for contract_position in contract.positions:
				if contract_position.state != 'open': continue
				
				# If needed, prepare a new invoice, if not already defined
				if not invoice_id:
					invoice_ids = invoices.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ], context=context )
					if invoice_ids and len(invoice_ids): invoice_id = invoice_ids[0]
				if not invoice_id:
					vals = self.get_invoice_default_values( cr, uid, contract, context=context )
					invoice_id = invoices.create( cr, uid, vals, context=context )
					if not invoice_id: break
				if not invoice:
					invoice = invoices.browse( cr, uid, invoice_id, context=context )
					if not invoice:
						invoice_id = False
						break

				now = datetime.now().strftime( '%Y-%m-%d' )
				if contract_position.next_invoice_date and contract_position.next_invoice_date > now:
					continue
				
				# Prepare a new invoice line
				do_it = True
				invoice_line_id = False
				if not contract_position.is_billable:
					if not eagle_param.make_inv_lines_with_unbillables:
						do_it = False
						invoice_line_id = True
				if do_it:
					vals = self.get_invoice_line_default_values( cr, uid, invoice, contract, contract_position, context=context )
					vals['contract_position_id'] = contract_position.id
					netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "vals="+str(vals) )
					invoice_line_id = invoice_lines.create( cr, uid, vals, context=context )
				if invoice_line_id:
					contract_positions.write( cr, uid, contract_position.id, { 'state': 'done' }, context=context )
				netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "invoice_line_id="+str(invoice_line_id) )
			
			if contract.state == 'production':

				# This loop handles recurrent contract positions 
				#	- recurrent products may be put either in the same or in a different invoice, depending on
				#	  how much time has passed between the 1st invoice and 1st occurence of the recurrent product
				#	- each time an object is correctly added to an invoice, its state is set to 'done'
				for contract_position in contract.positions:
					if not contract_position.is_active: continue
					if not contract_position.recurrence_id: continue
					if contract_position.state != 'recurrent': continue
					if not contract_position.next_invoice_date: continue
	
					recurrence = recurrences.browse( cr, uid, contract_position.recurrence_id.id, context=context )
					if not recurrence:
						continue
	
					now = datetime.now().strftime( '%Y-%m-%d' )
					next = datetime.strptime( contract_position.next_invoice_date, '%Y-%m-%d' )
					dt = next - relativedelta( days=contract_position.cancellation_deadline )
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
					
					# If needed, prepare a new invoice, if not already defined
					if not invoice_id:
						invoice_ids = invoices.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ], context=context )
						if invoice_ids and len(invoice_ids): invoice_id = invoice_ids[0]
					if not invoice_id:
						vals = self.get_invoice_default_values( cr, uid, contract, context=context )
						invoice_id = invoices.create( cr, uid, vals, context=context )
						if not invoice_id: break
					if not invoice:
						invoice = invoices.browse( cr, uid, invoice_id, context=context )
						if not invoice:
							invoice_id = False
							break
					
					# Prepare a new invoice line
					do_it = True
					invoice_line_id = False
					if not contract_position.is_billable:
						if not eagle_param.make_inv_lines_with_unbillables:
							do_it = False
							invoice_line_id = True
					if do_it:
						vals = self.get_invoice_line_default_values( cr, uid, invoice, contract, contract_position, context=context )
						vals['contract_position_id'] = contract_position.id
						invoice_line_id = invoice_lines.create( cr, uid, vals, context=context )
					if invoice_line_id:
						txt = contract_position.description + ' - ' + next.strftime( '%d.%m.%Y' ) + ' ' + _( 'to' ) + ' ' + after.strftime( '%d.%m.%Y' )
						contract_positions.write( cr, uid, contract_position.id, { 'next_invoice_date': after.strftime( '%Y-%m-%d' ), 'out_description': txt } )

			eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
			if eagle_param and eagle_param.auto_production_state:
				valid = True
				for cnt_line in contract.positions:
					if cnt_line.state == 'open':
						valid = False
						break
				if valid:
					self.contract_production( cr, uid, [contract.id], {} )
		
		return True

	def button_make_invoice(self, cr, uid, ids, context={}):
		return self.do_contract_inv_installation( cr, uid, ids, context=context, force_invoicing=True )

	def run_inv_scheduler( self, cr, uid, context={} ):
		''' Runs Invoices scheduler.
		'''
		if not context:
			context={}
		
		self_name = 'Eagle Invoices Scheduler'
		for contract in self.browse( cr, uid, self.search( cr, uid, [], context=context ), context=context ):
			if contract.state in ['installation','production']:
				netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "Checking contract '%s'" % contract.name )
				self.button_make_invoice( cr, uid, [contract.id], context=context )
		
		return True

eagle_contract()
