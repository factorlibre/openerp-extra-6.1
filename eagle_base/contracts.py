# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_base
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

class eagle_contract_base( osv.osv ):
	_name = 'eagle.contract'
	_description = 'Contract'

	def __get_eagle_parameters( self, cr, uid, context={} ):
		params_obj = self.pool.get( 'eagle.config.params' )
		for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
			return params

		return False
	
	def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if field_name == 'eagle_parm_auto_production_state':
			val = True
			if eagle_param:
				val = eagle_param.auto_production_state
				
			for pos_id in pos_ids:
				res[pos_id] = val

		return res
		
	_columns = {
		'name': fields.char( 'Contract', type='char', size=64, required=True ),
	}

	def __init__(self, pool, cr):
		super( eagle_contract_base, self ).__init__(pool, cr)
		funcs = [ 
			('draft','do_contract_base_draft'),
			('inst','do_contract_base_installation'),
			('prod','do_contract_base_production'),
			('closed','do_contract_base_close') ]
		for func_item in funcs:
			self.register_event_function( cr, 'Eagle Base', func_item[0], func_item[1] )

	def register_event_function( self, cr, module_descr, cfg_event_name, function_name ):
		uid = 1
		if 'eagle.config.event' not in self.pool.obj_pool:
			return False

		cfg_events = self.pool.get('eagle.config.event')
		cfg_event_ids = cfg_events.search( cr, uid, [('name','=',cfg_event_name)] )
		if cfg_event_ids and len(cfg_event_ids):
			cfg_event_id = cfg_event_ids[0]
		else:
			cfg_event_id = cfg_events.create( cr, uid, {'name':cfg_event_name} )
		if not cfg_event_id: return False
		found = False
		cfg_event = cfg_events.browse( cr, uid, cfg_event_id )
		if not cfg_event: return False
		for line in cfg_event.lines:
			if line.function_name == function_name:
				found = True
				break
		if not found:
			vals = {
				'name': cfg_event_id,
				'function_name': function_name,
				'seq': len(cfg_event.lines),
				'module_descr': module_descr,
			}
			self.pool.get( 'eagle.config.event.line' ).create( cr, uid, vals )
		return True

	# Start the installation
	def do_contract_base_installation( self, cr, uid, ids, context ):
		self.write( cr,uid,ids,{'state':'installation'}, context=context )
		return True

	# Start the production
	def do_contract_base_production( self, cr, uid, ids, context ):
		self.write( cr,uid,ids,{'state':'production'}, context=context )
		return True

	# Close the contract
	def do_contract_base_close( self, cr, uid, ids, context ):
		self.write( cr,uid,ids,{'state':'closed'}, context=context )
		return True

	# Start an offer
	def do_contract_base_draft( self, cr, uid, ids, context ):
		self.write( cr,uid,ids,{'state':'draft'}, context=context )
		return True

	# Generic function, used to react to all Eagle Config based events
	def handle_event( self, cr, uid, ids, cfg_event_name, context ):
		ret = True
		cfg_events = self.pool.get('eagle.config.event')
		cfg_event_ids = cfg_events.search( cr, uid, [('name','=',cfg_event_name)], context=context )
		if cfg_event_ids and len(cfg_event_ids):
			cfg_event = cfg_events.browse( cr, uid, cfg_event_ids[0], context=context )
			if cfg_event:
				for cfg_event_line in cfg_event.lines:
					# Determine if self has at least a member with a name stored in the event config. line
					if not hasattr(self,cfg_event_line.function_name): continue
					# Determine if the newly detected member is a function or not
					func = getattr(self,cfg_event_line.function_name)
					if not hasattr(func,'__call__'): continue
					#  Yes, call it!!
					if func(cr, uid, ids, context):
						ret = True
		
		return ret
		
	# This handles the automatic state changes, if active in Eagle's parameters
	def check_state( self, cr, uid, contract_ids, context={} ):
		if isinstance( contract_ids, (int,long) ): contract_ids = [contract_ids]

		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if not eagle_param or not eagle_param.auto_production_state or len(contract_ids) < 1:
			return False

		ret = False

		# As of vers. 4.7.01+, a contract in "Installation" state with no position to install
		# and if it's set in Eagle's configuration, is automatically change to "Production"
		to_do = []
		for cnt in self.browse( cr, uid, contract_ids, context=context ):
			if cnt.state != 'installation': continue
			add_it = True
			for pos in cnt.positions:
				if pos.state == 'open':
					add_it = False
					break
			if add_it:
				to_do.append(cnt.id)
		if len(to_do)> 0:
			ret = self.handle_event( cr, uid, to_do, 'prod', context )
		
		return ret

	# Response to the "Set to Draft" button
	def contract_draft( self, cr, uid, ids, context ):
		return self.handle_event( cr, uid, ids, 'draft', context )

	# Response to the "Set to Installation State" button
	def contract_installation( self, cr, uid, ids, context ):
		ret = self.handle_event( cr, uid, ids, 'inst', context )
		self.check_state( cr, uid, ids, context=context )
		
		return ret

	# Response to the "Set to Production State" button
	def contract_production( self, cr, uid, ids, context ):
		return self.handle_event( cr, uid, ids, 'prod', context )

	# Response to the "Set to Closed State" button
	def contract_close( self, cr, uid, ids, context ):
		return self.handle_event( cr, uid, ids, 'closed', context )

eagle_contract_base()

class eagle_contract_pos(osv.osv):
	_name = 'eagle.contract.position'
	_description = 'Contract position'

	def _warranty_near_the_end( self, cr, uid, pos_ids, name, args, context ):
		res = {}
		for pos_id in pos_ids:
			res[pos_id] = False
			pos = self.browse( cr, uid, pos_id, context=context )
			if not pos: continue
			if not pos.warranty_state or pos.warranty_state == 'none': continue
			if not pos.warranty_id: continue
			if not pos.warranty_date_limit or not pos.warranty_end_date: continue
			now = datetime.now().strftime( '%Y-%m-%d' )
			if pos.warranty_date_limit <= now and now <= pos.warranty_end_date:
				res[pos_id] = True
		
		return res
		
	def _amount_line_base(self, cr, uid, line_ids, field_name, arg, context=None):
		res = {}
		if context is None:
			context = {}
		
		for line in self.browse(cr, uid, line_ids, context=context):
			if line.is_billable and field_name == 'cl_total':
				price = line.list_price
				res[line.id] = price * line.qty
			else:
				res[line.id] = 0.0
		
		return res

	def __get_eagle_parameters( self, cr, uid, context={} ):
		params_obj = self.pool.get( 'eagle.config.params' )
		for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
			return params

		return False
	
	def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if field_name == 'eagle_parm_use_price':
			val = True
			if eagle_param:
				val = eagle_param.use_prices
				
			for pos_id in pos_ids:
				res[pos_id] = val

		return res

	_columns = {
		'name': fields.many2one( 'product.product', 'Product', required=True ),
		'qty': fields.float( 'Quantity' ),
		'contract_id': fields.many2one( 'eagle.contract', 'Contract', required=True ),
		'recurrence_id': fields.many2one( 'product.recurrence.unit', 'Recurrence' ),
		'next_invoice_date': fields.date( 'Next Action Date' ),
		'state': fields.selection( [
				( 'open','To install' ),
				( 'done','Installed' ),
				( 'recurrent','Recurrent' ),
				], 'State' ),
		'cancellation_deadline': fields.integer( 'Days before' ),
		'is_active': fields.boolean( 'Active' ),
		'is_billable': fields.boolean( 'Billable?' ),
		'sequence': fields.integer('Sequence'),
		'description': fields.char( 'Description', type='char', size=250 ),
		'out_description': fields.char('Reported text', size=256),
		'warranty_state': fields.selection( [
			( 'none','None' ),
			( 'basic', 'Basic' ),
			( 'extended', 'Extended' ), 
			] , 'Warranty State', required=True),
		'warranty_id': fields.many2one( 'eagle.warranty', 'Warranty' ),
		'warranty_end_date': fields.date( 'End of warranty' ),
		'warranty_end_days': fields.integer( 'Days before the end' ),
		'warranty_date_limit': fields.date( 'Warranty limit' ),
		'warranty_near_the_end': fields.function( _warranty_near_the_end, method=True, type='boolean', string="Warranty near the end?" ),
		'eagle_parm_use_price': fields.function( _eagle_params, method=True, type='boolean', string="Uses prices?" ),
		'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Sale Price'), help="Base price for computing the customer price."),
		'cl_total': fields.function( _amount_line_base, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
		'notes': fields.text( 'Notes' ),
	}

	_defaults = {
		'state': 'open',
		'sequence': 1,
		'warranty_state': lambda *a:'none',
		'warranty_end_days': lambda *a:30,
		'is_billable': lambda *a:True,
		'eagle_parm_use_price': lambda *a:True,
	}

	_order = 'sequence,id'

	def recomp_line(self, cr, uid, ids, product, customer, qty, list_price):
		if not product or not customer: return False

		return { 'value': {
			'cl_total': qty * list_price,
		} }

	def onchange_description(self, cr, uid, ids, description, recurrence_id, next_invoice_date):
		txt = tools.ustr(description)
		if not next_invoice_date or not recurrence_id:
			return {
			'value': { 'out_description': txt }
		}
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		start_date = datetime.strptime( next_invoice_date, '%Y-%m-%d' )
		end_date = start_date
		recurrence = self.pool.get( 'product.recurrence.unit' ).browse( cr, uid, recurrence_id )
		if recurrence:
			if recurrence.unit == 'day':
				end_date = start_date + relativedelta( days=recurrence.value )
			elif recurrence.unit == 'month':
				end_date = start_date + relativedelta( months=recurrence.value )
			elif recurrence.unit == 'year':
				end_date = start_date + relativedelta( years=recurrence.value )
			if recurrence.value > 0:
				end_date -= relativedelta( days=1 )
			if txt:
				if txt != '': txt += ' - '
			else:
				txt = ''
			txt += start_date.strftime( '%d.%m.%Y' ) + ' ' + _( 'to' ) + ' ' + end_date.strftime( '%d.%m.%Y' )
		
		return {
			'value': { 'out_description': txt }
		}

	def onchange_recurrence(self, cr, uid, ids, recurrence_id):
		res = { 'qty': 1 }
		if not recurrence_id:
			res['state'] = 'open'
			res['cancellation_deadline'] = False
			res['next_invoice_date'] = False
		else:
			recurrence = self.pool.get( 'product.recurrence.unit' ).browse( cr, uid, recurrence_id )
			if recurrence:
				now = datetime.now().strftime( '%Y-%m-%d' )
				if recurrence.unit == 'day':
					next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( days=recurrence.value )
					if recurrence.value > 0:
						next -= relativedelta( days=1 )
					res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
					res['state'] = 'recurrent'
					res['cancellation_deadline'] = 30
					res['is_active'] = True
				elif recurrence.unit == 'month':
					next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( months=recurrence.value )
					if recurrence.value > 0:
						next -= relativedelta( days=1 )
					res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
					res['state'] = 'recurrent'
					res['cancellation_deadline'] = 30
					res['is_active'] = True
				elif recurrence.unit == 'year':
					next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( years=recurrence.value )
					if recurrence.value > 0:
						next -= relativedelta( days=1 )
					res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
					res['state'] = 'recurrent'
					res['cancellation_deadline'] = 30
					res['is_active'] = True
		
		return {
			'value': res
		}
		
	def onchange_product(self, cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id):
		res = {}
		if not product_id:
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "Eagle Base's onchange_product() is returning nothing because there's no product id" )
			return { 'value': {} }
		
		prod = self.pool.get('product.product').browse(cr, uid, product_id)
		if not prod:
			raise osv.except_osv(_('Error !'), _('Product not found.'))
			
		res['description'] = prod.name
		res['notes'] = prod.description_sale
		if not qty or qty == 0.0:
			qty = 1.0
			res['qty'] = qty

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
		else:
			delay = prod.sale_delay or False

		# 2011-06-28/Cyp/Jae moved to Eagle Management
		#res['product_duration'] = delay
		res['list_price'] = prod.list_price

		if not prod.recurrence_id:
			res['state'] = 'open'
			res['recurrence_id'] = False
			res['cancellation_deadline'] = 0
			res['next_invoice_date'] = False
			res['is_active'] = False
		else:
			res['state'] = 'recurrent'
			res['recurrence_id'] = prod.recurrence_id.id
			res['cancellation_deadline'] = 30
			res['is_active'] = True
			if not date_start:
				if prod.recurrence_id.unit == 'day':
					date_start = datetime.strftime( '%Y-%m-%d' ) + relativedelta( days=1 )
				else:
					date_start = datetime.strftime( '%Y-%m-1' ) + relativedelta( months=1 )
			res['next_invoice_date'] = date_start
			next = False
			if prod.recurrence_id.unit == 'day':
				next = datetime.strptime( date_start, '%Y-%m-%d' ) + relativedelta( days=prod.recurrence_id.value ) 
			elif prod.recurrence_id.unit == 'month':
				next = datetime.strptime( date_start, '%Y-%m-%d' ) + relativedelta( months=prod.recurrence_id.value )
			elif prod.recurrence_id.unit == 'year':
				next = datetime.strptime( date_start, '%Y-%m-%d' ) + relativedelta( years=prod.recurrence_id.value )
			if next:
				if prod.recurrence_id.value > 0:
					next -= relativedelta( days=1 )
				res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
			
		if pricelist_id and partner_id:
			price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
						prod.id, qty or 1.0, partner_id, {
							'uom': prod.uom_id.id,
							'date': date_start,
							})[pricelist_id]
			if price:
				res.update({'list_price': price})
		res.update( { 'cl_total': qty * res['list_price'] } )

		vals = self.onchange_description( cr, uid, ids, res['description'], res['recurrence_id'], res['next_invoice_date'] )
		res.update( vals['value'] )

		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "Eagle Base's onchange_product() is returning: "+str(res) )
		return { 'value': res }

	def button_disable(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'is_active':False} )
		return True

	def button_enable(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'is_active':True} )
		return True

	def create(self, cr, uid, vals, context=None):
		war_end_days = vals['warranty_end_days']
		war_end_date = vals['warranty_end_date']
		if war_end_days and war_end_date:
			dt = datetime.strptime(war_end_date,'%Y-%m-%d' ) + relativedelta( days=-war_end_days )
			vals['warranty_date_limit'] = dt.strftime( '%Y-%m-%d' )
		
		return super( eagle_contract_pos, self ).create( cr, uid, vals, context=context )

	def write(self, cr, uid, pos_ids, vals, context=None):
		contracts = []
		if isinstance(pos_ids, (int, long)):
			pos_ids = [pos_ids]
		for pos in self.browse( cr, uid, pos_ids, context=context ):
			if pos.contract_id:
				contracts.append( pos.contract_id.id )
			war_end_days = 'warranty_end_days' in vals and vals['warranty_end_days'] or pos.warranty_end_days
			war_end_date = 'warranty_end_date' in vals and vals['warranty_end_date'] or pos.warranty_end_date
			if war_end_days and war_end_date:
				dt = (datetime.strptime(war_end_date, '%Y-%m-%d' ) + relativedelta( days=-war_end_days ))
				vals['warranty_date_limit'] = dt.strftime( '%Y-%m-%d' )
			break
		
		ret = super( eagle_contract_pos, self ).write( cr, uid, pos_ids, vals, context=context )
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if eagle_param and eagle_param.auto_production_state and len(contracts) > 0 and 'state' in vals:
			self.pool.get( 'eagle.contract' ).check_state( cr, uid, contracts, context=context )
		
		return ret

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = super(eagle_contract_pos, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		use_prices = True
		if eagle_param:
			use_prices = eagle_param.use_prices
		if not use_prices:
			i = 0
			lst = res['arch'].split('\n')
			while (i < len(lst)):
				if 'cl_amount' in lst[i]:
					lst[i] = """<field name="cl_amount" invisible="1"/>"""
				elif 'cl_taxes' in lst[i]:
					lst[i] = """<field name="cl_taxes" invisible="1"/>"""
				elif 'cl_total' in lst[i]:
					lst[i] = """<field name="cl_total" invisible="1"/>"""
				i += 1
			res['arch'] = '\n'.join(lst)

		return res

eagle_contract_pos()

def format_date_tz(date, tz=None):
	if not date:
		return 'n/a'
	format = tools.DEFAULT_SERVER_DATETIME_FORMAT
	return tools.server_to_local_timestamp(date, format, format, tz)

class eagle_contract_message( osv.osv ):
	_name = 'eagle.contract.message'
	_description = 'History item for contracts'
	
	def truncate_data(self, cr, uid, data, context=None):
		data_list = data and data.split('\n') or []
		if len(data_list) > 3:
			res = '\n\t'.join(data_list[:3]) + '...'
		else:
			res = '\n\t'.join(data_list)
		return res
		
	def buid_display_text(self, cr, uid, msg, user_name, msg_date, context={}):
		tz = context.get('tz', ('Europe','Europe'))
		msg_txt = (user_name or '/') + _(' has added this note on ') + format_date_tz(msg_date, tz) + ':\n\t'
		msg_txt += self.truncate_data(cr, uid, msg, context=context)
		
		return msg_txt

	def _get_display_text(self, cr, uid, ids, name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		for message in self.browse(cr, uid, ids, context=context):
			result[message.id] = self.buid_display_text(cr, uid, message.description, message.user_id.name, message.date, context=context)
		return result

	_columns = {
		'date': fields.datetime('Date'),
		'user_id': fields.many2one('res.users', 'User Responsible', readonly=True),
		'description': fields.text('Description'),
		'display_text': fields.function(_get_display_text, method=True, type='text', size="512", string='Messages', store=False),
		'contract_id': fields.many2one( 'eagle.contract', 'Contract', required=True ),
	}
	
	_defaults = {
		'date': time.strftime('%Y-%m-%d %H:%M:%S'),
		'user_id': lambda self,cr,uid,context: uid,
	}

	def onchange_msg_txt(self, cr, uid, ids, msg, user_id, msg_date):
		res = {  }
		user_obj = self.pool.get( 'res.users' ).browse( cr, uid, user_id )
		res['display_text'] = self.buid_display_text(cr, uid, msg, user_obj and user_obj.name or '/', msg_date)
		
		return {
			'value': res
		}

eagle_contract_message()

class eagle_contract( osv.osv ):
	_inherit = 'eagle.contract'
	_eagle_view_selection_account_visible = False

	def get_view_selections(self, cr, uid, context={}):
		# The result looks like this:
		#	[('contract', 'Contract'), ('account', 'Accounting'), ('crm', 'CRM'), ('moves', 'Stock Moves')]
		lst = [('contract','Contract')]
		if self._eagle_view_selection_account_visible:
			lst += [('account','Accounting')]

		return lst

	def _get_view_select_is_visible( self, cr, uid, ids, name, args, context={} ):
		res = {}
		lst = self.get_view_selections(cr, uid, context=context)
		vis = len(lst) > 1
		for id in ids:
			res[id] = vis

		return res

	def _get_cl_total_base( self, cr, uid, cnt_ids, name, args, context={} ):
		res = {}
		for cnt in self.browse( cr, uid, cnt_ids, context=context ):
			tot = 0.0
			for cl in cnt.positions:
				tot += cl.cl_total
			res[cnt.id] = tot
		
		return res
	
	def __get_eagle_parameters( self, cr, uid, context={} ):
		params_obj = self.pool.get( 'eagle.config.params' )
		for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
			return params

		return False
	
	def _eagle_params( self, cr, uid, cnt_ids, field_name, args, context={} ):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if field_name == 'eagle_view_selection_account_visible':
			val = self._eagle_view_selection_account_visible

		if field_name == 'eagle_parm_use_price':
			val = True
			if eagle_param:
				val = eagle_param.use_prices
				
		if field_name == 'eagle_parm_use_members_list':
			val = True
			if eagle_param:
				val = eagle_param.use_members_list
				
		if field_name == 'eagle_parm_show_all_meta_tabs':
			val = False
			if eagle_param:
				val = eagle_param.show_all_meta_tabs
				
		if field_name == 'eagle_parm_auto_production_state':
			val = True
			if eagle_param:
				val = eagle_param.auto_production_state
				
		for cnt_id in cnt_ids:
			res[cnt_id] = val

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
		'date_start': fields.date( 'Start Date', required=True ),
		'date_end': fields.date( 'End Date' ),
		'state': fields.selection( [
				( 'draft','Offer' ),
				( 'installation','Installation' ),
				( 'production','Production' ),
				( 'closed','Closed' ),
				], 'Contract State' ),
		'customer_id': fields.many2one( 'res.partner', 'Customer', required=True ),
		'user_id': fields.many2one( 'res.users', 'Salesman', readonly=True ),
		'positions': fields.one2many( 'eagle.contract.position', 'contract_id', 'Positions' ),
		'financial_partner_id': fields.many2one( 'res.partner', 'Funded by' ),
		'message_ids': fields.one2many('eagle.contract.message', 'contract_id', 'Messages'),
		'request_ids': fields.one2many('res.request', 'contract_id', 'Requests'),
		'warranty_near_the_end': fields.boolean( "Near end of Warranty" ),
		'members': fields.many2many('res.users', 'eagle_contract_user_rel', 'contract_id', 'uid', 'Contract Members'),
		'view_selection': fields.selection( get_view_selections, 'View selection' ),
		'view_select_is_visible': fields.function( _get_view_select_is_visible, method=True, type='boolean', string="View selection visible?" ),
		'eagle_parm_use_price': fields.function( _eagle_params, method=True, type='boolean', string="Uses prices?" ),
		'pricelist_id': fields.many2one('product.pricelist', 'Pricelist' ),
		'c_total': fields.function( _get_cl_total_base, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
		'eagle_parm_use_members_list': fields.function( _eagle_params, method=True, type='boolean', string="Uses members list?" ),
		'eagle_parm_show_all_meta_tabs': fields.function( _eagle_params, method=True, type='boolean', string="Show all meta-tabs?" ),
		'eagle_view_selection_account_visible': fields.function( _eagle_params, method=True, type='boolean', string="Accounting button visible?" ),
		'activeTab_contract': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: contract" ),
		'activeTab_account': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: account" ),
	}

	_defaults = {
		'state': lambda *a:'draft',
		'user_id': lambda self,cr,uid,context: uid,
		'date_start': datetime.now().strftime( '%Y-%m-%d' ),
		'name': 'no name',
		'view_selection': lambda *a:'contract',
	}

	def _warranty_near_the_end( self, cr, uid, cnt_id, context ):
		res = False
		if not cnt_id: return False
		now = datetime.now().strftime( '%Y-%m-%d' )
		cnt = self.browse( cr, uid, cnt_id, context=context )
		if not cnt: return False
		for pos in cnt.positions:
			if not pos.warranty_state or pos.warranty_state == 'none': continue
			if not pos.warranty_id: continue
			if not pos.warranty_date_limit or not pos.warranty_end_date: continue
			if pos.warranty_date_limit <= now and now <= pos.warranty_end_date:
				return True
		
		return False
	
	def create(self, cr, uid, vals, context=None):
		ret_id = super( eagle_contract, self ).create( cr, uid, vals, context=context )
		if ret_id:
			wr_near_end = self._warranty_near_the_end( cr, uid, ret_id, context=context )
			super( eagle_contract, self ).write( cr, uid, ret_id, { 'warranty_near_the_end': wr_near_end }, context=context )
		return ret_id

	def write(self, cr, uid, cnt_ids, vals, context=None):
		ret = super( eagle_contract, self ).write( cr, uid, cnt_ids, vals, context=context )
		
		if isinstance(cnt_ids, (int, long)):
			cnt_ids = [cnt_ids]
		for cnt_id in cnt_ids:
			wr_near_end = self._warranty_near_the_end( cr, uid, cnt_id, context=context )
			super( eagle_contract, self ).write( cr, uid, cnt_ids, { 'warranty_near_the_end': wr_near_end }, context=context )
			break
		
		return ret

	def unlink(self, cr, uid, ids, context=None):
		contracts = self.read(cr, uid, ids, ['state','positions'], context=context)
		unlink_parent_ids = []
		unlink_children_ids = []
		for c in contracts:
			if c['state'] in ['draft']:
				unlink_parent_ids.append(c['id'])
				if len( c['positions'] ) > 0:
					unlink_children_ids += c['positions']
			else:
				raise osv.except_osv( _('Invalid action !'), 
					_('Cannot delete contract(s) which are already confirmed !') )
		if len( unlink_children_ids ) > 0:
			self.pool.get( 'eagle.contract.position' ).unlink( cr, uid, unlink_children_ids, context=context )
		return osv.osv.unlink( self, cr, uid, unlink_parent_ids, context=context )

	def copy(self, cr, uid, id, default={}, context={}):
		# !!!!!!!!!!!!!!!!!!
		# The default COPY function tries to copy everything, including one2many stuff
		# which may be completely weird for contract's leads because it tries to copy
		# the adresses as well
		# Solution: create a new record with some of the original's values

		contract = self.browse( cr, uid, id, context=context )
		contract_positions = self.pool.get( 'eagle.contract.position' )

		context_wo_lang = context.copy()
		if 'lang' in context:
			del context_wo_lang['lang']
		data = self.read(cr, uid, [id,], context=context_wo_lang)
		if data:
			data = data[0]
		else:
			raise IndexError( _("Record #%d of %s not found, cannot copy!") %( id, self._name))
		fields = self.fields_get(cr, uid, context=context)
		for f in fields:
			if self._log_access and f in ('create_date', 'create_uid', 'write_date', 'write_uid'):
				del data[f]
			if 'function' in fields[f]:
				del data[f]
				continue
			ftype = fields[f]['type']
			if ftype == 'many2one':
				if fields[f].get('required', False):
					try:
						data[f] = data[f] and data[f][0]
					except:
						pass
				else:
					data[f] = False
				
			elif ftype in ('one2many', 'one2one'):
				data[f] = []
			elif ftype == 'many2many':
				data[f] = [(6,0,[])]
		del data['id']
		data['name'] = contract.name+ _(' (copy)')
		data['state'] = 'draft'
		# Recopy some MANY2ONE attributes
		for attr in ['customer_id','financial_partner_id','pricelist_id','user_id']:
			if not hasattr( contract, attr ): continue
			value = getattr( contract, attr )
			data[attr] = value and value.id or False
		# Recopy some MANY2MANY attributes
		for attr in ['members']:
			if not hasattr( contract, attr ): continue
			values = getattr( contract, attr )
			if values:
				data[attr] = [(6,0,[ x.id for x in values ])]
		netsvc.Logger().notifyChannel("Contract copy", netsvc.LOG_DEBUG, "Info: data[]="+str(data))
		
		new_contract_id = self.create( cr, uid, data, context=context ) 

		# Let's copy the contract positions
		for pos in contract.positions:
			vals = {
				'contract_id': new_contract_id, 
				'state': pos.state == 'recurrent' and 'recurrent' or 'open'
			}
			new_pos_id = contract_positions.copy( cr, uid, pos.id, vals, context=context )
			
		return new_contract_id

	# Activate the "Contract" tabs
	def button_view_contract(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'view_selection':'contract'} )
		return True

	# Activate the "Accounting" tabs
	def button_view_accounting(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'view_selection':'account'} )
		return True

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = super(eagle_contract, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
		return res

	def onchange_customer(self, cr, uid, ids, customer_id):
		res = { }
		if customer_id:
			cust = self.pool.get( 'res.partner' ).browse( cr, uid, customer_id )
			if cust:
				if cust.property_product_pricelist:
					res['pricelist_id'] = cust.property_product_pricelist.id
				if hasattr(cust, 'ons_hrtif_to_invoice') and cust.ons_hrtif_to_invoice:
					res['ons_hrtif_to_invoice'] = cust.ons_hrtif_to_invoice.id
		return {
			'value': res
		}

	def button_cyp_debug(self, cr, uid, ids, context={}):
		val=self.get_view_selections(cr, uid, context=context)
		netsvc.Logger().notifyChannel("Cyp:debug called", netsvc.LOG_DEBUG, "val="+str(val))
		return True

eagle_contract()

class eagle_customer( osv.osv ):
	_name = 'eagle.customer'
	_description = 'Contracts Customers'
	_auto = False
	_rec_name = 'customer_id'

	_columns = {
		'customer': fields.char( 'Customer', size=128, readonly=True),
		'nb_contracts': fields.integer( 'Contracts Nb', readonly=True),
	}
	_order = 'customer'

	def init(self, cr):
		tools.sql.drop_view_if_exists(cr, 'eagle_customer')
		cr.execute( 'CREATE OR REPLACE VIEW eagle_customer AS (' \
				'SELECT DISTINCT ' \
				'customer_id AS id, res_partner.name as customer, count(eagle_contract.id) as nb_contracts ' \
				'FROM eagle_contract, res_partner ' \
				'where customer_id=res_partner.id ' \
				'group by res_partner.name, customer_id ' \
				'order by res_partner.name )' )

eagle_customer()
