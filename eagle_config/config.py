# -*- coding: utf-8 -*-
#
#  File: config.py
#  Module: eagle_config
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
import tools
from tools.translate import _

class eagle_config_event_base( osv.osv ):
	_name = 'eagle.config.event'
	_description = 'Eagle Events management'

	_columns = {
		'name': fields.selection( [
			('draft', 'Draft'),
			('inst', 'Installation'),
			('prod', 'Production'),
			('closed', 'Closed'),
			], 'Linked to', required=True ),
	}
	
	_defaults = {
		'name': lambda *a:'draft',
	}
	
	_order = 'name'

eagle_config_event_base()

class eagle_config_event_line( osv.osv ):
	_name = 'eagle.config.event.line'

	_columns = {
		'name': fields.many2one( 'eagle.config.event', string='Event name' ),
		'seq': fields.integer( 'Pos' ),
		'function_name': fields.char( 'Function name', size=100 ),
		'module_descr': fields.char( 'Module', size=64 ),
	}
	
	_defaults = {
		'seq': lambda *a:0,
	}
	
	_order = 'seq,id'

eagle_config_event_line()

class eagle_config_event( osv.osv ):
	_inherit = 'eagle.config.event'

	_columns = {
		'lines': fields.one2many( 'eagle.config.event.line', 'name', 'Lines' ),
	}
	
eagle_config_event()

class eagle_config_params( osv.osv ):
	_name = 'eagle.config.params'
	description = 'Eagle Configuration Parameters'
	
	def _detect_smtp_ok(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		if context is None:
			context = {}

		ret = True
		if not tools.config.get('smtp_server'):
			ret = False

		for id in ids:
			res[id] = ret

		return res

	_columns = {
		'name': fields.char( 'Name', size=40 ),
		'use_prices': fields.boolean( 'Uses price', help='If True, the contract and its position will display the prices and the amounts.' ),
		'use_members_list': fields.boolean( 'Uses members list', help='If True, the contract will display the list of members' ),
		'send_mail_with_request': fields.boolean( 'Validating a request sends an email' ),
		'smtp_ok': fields.function( _detect_smtp_ok, method=True, type='boolean', string='SMTP server defined?', store=False ),
		'show_all_meta_tabs': fields.boolean( 'Show all meta-tabs?' ),
		'auto_production_state': fields.boolean( "Automatic 'Production state' mode?" ),
		'tabs': fields.char( 'Tabs list', size=250 ),
		'void': fields.char( ' ', size=1 ),
	}
	
	_defaults = {
		'name': lambda *a: 'Eagle Parameters',
		'use_prices': lambda *a: True, 
		'use_members_list': lambda *a: False, 
		'send_mail_with_request': lambda *a: False, 
		'auto_production_state': lambda *a: True, 
		'void': lambda *a: ' ',
	}

	_sql_constraints = [
		('eagle_param_uniq', 'unique (name)', 'Only one configuration for Eagle!')
	]

	def copy(self, cr, uid, id, default={}, context={}):
		raise osv.except_osv(_('Forbidden!'), _('Eagle must have one and only one record.'))

eagle_config_params()
