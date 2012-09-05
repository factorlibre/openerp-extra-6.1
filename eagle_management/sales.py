# -*- coding: utf-8 -*-
#
#  File: sales.py
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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from tools.translate import _
import decimal_precision as dp

class sale_order( osv.osv ):
	_inherit = 'sale.order'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		# This field is automatically set at the moment when a contract is set to "open"
		# Else, it's always False. Sale order and invoice report will be set accordingly.
		'financial_partner_id': fields.many2one( 'res.partner', 'Funded by' ),
	}

	def _make_invoice(self, cr, uid, order, lines, context=None):
		journal_obj = self.pool.get('account.journal')
		inv_obj = self.pool.get('account.invoice')
		obj_invoice_line = self.pool.get('account.invoice.line')
		if context is None:
			context = {}

		journal_ids = journal_obj.search(cr, uid, [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)], limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error !'),
				_('There is no sale journal defined for this company: "%s" (id:%d)') % (order.company_id.name, order.company_id.id))
		a = order.partner_id.property_account_receivable.id
		if order.payment_term:
			pay_term = order.payment_term.id
		else:
			pay_term = False
		invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
		from_line_invoice_ids = []
		for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
			for invoice_line_id in invoiced_sale_line_id.invoice_lines:
				if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
					from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
		for preinv in order.invoice_ids:
			if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
				for preline in preinv.invoice_line:
					inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
					lines.append(inv_line_id)
		inv = {
			'name': order.client_order_ref or order.name,
			'origin': order.name,
			'type': 'out_invoice',
			'reference': "P%dSO%d" % (order.partner_id.id, order.id),
			'account_id': a,
			'partner_id': order.partner_id.id,
			'journal_id': journal_ids[0],
			'address_invoice_id': order.partner_invoice_id.id,
			'address_contact_id': order.partner_order_id.id,
			'invoice_line': [(6, 0, lines)],
			'currency_id': order.pricelist_id.currency_id.id,
			'comment': order.note,
			'payment_term': pay_term,
			'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
			'date_invoice': context.get('date_invoice',False),
			'company_id': order.company_id.id,
			'user_id':order.user_id and order.user_id.id or False,
			'contract_id':order.contract_id and order.contract_id.id or False,
			'financial_partner_id':order.financial_partner_id and order.financial_partner_id.id or False,
		}
		inv.update(self._inv_get(cr, uid, order))
		inv_id = inv_obj.create(cr, uid, inv, context=context)
		data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], pay_term, time.strftime('%Y-%m-%d'))
		if data.get('value', False):
			inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
		inv_obj.button_compute(cr, uid, [inv_id])

		return inv_id

	def action_ship_create(self, cr, uid, ids, *args):
		wf_service = netsvc.LocalService("workflow")
		picking_id = False
		move_obj = self.pool.get('stock.move')
		proc_obj = self.pool.get('procurement.order')
		company = self.pool.get('res.users').browse(cr, uid, uid).company_id
		for order in self.browse(cr, uid, ids, context={}):
			proc_ids = []
			output_id = order.shop_id.warehouse_id.lot_output_id.id
			picking_id = False
			for line in order.order_line:
				proc_id = False
				date_planned = False
				if line.contract_pos_id:
					date_planned = line.contract_pos_id.stock_disposal_date
				if not date_planned:
					date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
					date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')

				if line.state == 'done':
					continue
				move_id = False
				if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
					location_id = order.shop_id.warehouse_id.lot_stock_id.id
					if not picking_id:
						pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
						picking_id = self.pool.get('stock.picking').create(cr, uid, {
							'name': pick_name,
							'origin': order.name,
							'type': 'out',
							'state': 'auto',
							'move_type': order.picking_policy,
							'sale_id': order.id,
							'address_id': order.partner_shipping_id.id,
							'note': order.note,
							'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
							'company_id': order.company_id.id,
						})
					move_id = self.pool.get('stock.move').create(cr, uid, {
						'name': line.name[:64],
						'picking_id': picking_id,
						'product_id': line.product_id.id,
						'date': date_planned,
						'date_expected': date_planned,
						'product_qty': line.product_uom_qty,
						'product_uom': line.product_uom.id,
						'product_uos_qty': line.product_uos_qty,
						'product_uos': (line.product_uos and line.product_uos.id)\
								or line.product_uom.id,
						'product_packaging': line.product_packaging.id,
						'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
						'location_id': location_id,
						'location_dest_id': output_id,
						'sale_line_id': line.id,
						'tracking_id': False,
						'state': 'draft',
						#'state': 'waiting',
						'note': line.notes,
						'company_id': order.company_id.id,
						'returned_price': line.price_unit,
					})

				if line.product_id:
					proc_id = self.pool.get('procurement.order').create(cr, uid, {
						'name': line.name,
						'origin': order.name,
						'date_planned': date_planned,
						'product_id': line.product_id.id,
						'product_qty': line.product_uom_qty,
						'product_uom': line.product_uom.id,
						'product_uos_qty': (line.product_uos and line.product_uos_qty)\
								or line.product_uom_qty,
						'product_uos': (line.product_uos and line.product_uos.id)\
								or line.product_uom.id,
						'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
						'procure_method': line.type,
						'move_id': move_id,
						'property_ids': [(6, 0, [x.id for x in line.property_ids])],
						'company_id': order.company_id.id,
						'contract_id': order.contract_id and order.contract_id.id or False,
					})
					proc_ids.append(proc_id)
					self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
					if order.state == 'shipping_except':
						for pick in order.picking_ids:
							for move in pick.move_lines:
								if move.state == 'cancel':
									mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'),('sale_line_id', '=', line.id),('picking_id', '=', pick.id)])
									if mov_ids:
										for mov in move_obj.browse(cr, uid, mov_ids):
											move_obj.write(cr, uid, [move_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
											proc_obj.write(cr, uid, [proc_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})

			val = {}
			for proc_id in proc_ids:
				wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

			if picking_id:
				wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

			if order.state == 'shipping_except':
				val['state'] = 'progress'
				val['shipped'] = False

				if (order.order_policy == 'manual'):
					for line in order.order_line:
						if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
							val['state'] = 'manual'
							break
			self.write(cr, uid, [order.id], val)

		return True

sale_order()

class sale_order_line( osv.osv ):
	_inherit = 'sale.order.line'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'contract_pos_id': fields.many2one( 'eagle.contract.position', 'Contract Position' ),
	}

sale_order_line()
