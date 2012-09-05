# -*- coding: utf-8 -*-
#
#  File: wizard/crm_contact_to_lead.py
#  Module: eagle_crm
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
from tools.translate import _

class crm_contact2lead(osv.osv_memory):
	"""Converts Contact To Lead"""

	_name = 'eagle.contact2lead'
	_description = 'Contact To Lead'

	_columns = {
		'name': fields.char('Last Name', size=64, required=True),
		'description': fields.text('Notes'),
		'partner_contact_id': fields.many2one('res.partner.contact', 'Partner Contact'),
		'partner_id': fields.many2one('res.partner', 'Partner'),
		'user_id': fields.many2one('res.users', 'Salesman'),
		'type':fields.selection([('lead','Lead'),('opportunity','Opportunity'),],'Type', help="Type is used to separate Leads and Opportunities"),
		'priority': fields.selection([('1', 'Highest'),('2', 'High'),('3', 'Normal'),('4', 'Low'),('5', 'Lowest'),], 'Priority'),
		'section_id': fields.many2one('crm.case.section', 'Sales Team'),
		'lead_categ_id': fields.many2one('crm.case.categ', 'Category', domain="[('object_id.model', '=', 'crm.lead')]"),
		'type_id': fields.many2one('crm.case.resource.type', 'Campaign', domain="['|',('section_id','=',section_id),('section_id','=',False)]"),
		'channel_id': fields.many2one('res.partner.canal', 'Channel'),
		'active': fields.boolean('Active', required=False),
		'state':fields.selection([('step1','step1'),('step2','step2'),('step3','step3'),('step4','step4'),('step5','step5')], 'states', readonly=True),
	}

	_defaults = {
		'state': lambda *a: 'step1',
		'active': lambda *a: 1,
		'user_id': lambda self, cr, uid, ctx: uid,
		'partner_contact_id': lambda self, cr, uid, ctx: ctx and ctx.get('active_model','') == 'res.partner.contact' and ctx.get('active_id',False) or False,
		'partner_id': lambda self, cr, uid, ctx: ctx and 
			ctx.get('active_model','') == 'res.partner.contact' and 
			ctx.get('active_id',False) and
			self.pool.get('res.partner.contact').read(cr,uid,ctx['active_id'],['partner_id'],context=ctx)['partner_id']
			 or False,
		'type': lambda *a: 'lead',
		'lead_statut': lambda *a: 'running',
	}
	
	def go_step1(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step1'}, context=context)
		return True
	
	def go_step2(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step2'}, context=context)
		return True
	
	def make_lead(self, cr, uid, ids, context=None):
		"""
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param context: A standard dictionary for contextual values
		"""

		lead_obj = self.pool.get('crm.lead')
		
		for data in self.browse(cr, uid, ids):
			vals = {
				'name': data.name,
				'description': data.description,
				'active': data.active,
				'user_id': uid,
				'type': data.type,
				'priority': data.priority,
				'section_id': data.section_id and data.section_id.id or False,
				'partner_id': data.partner_id and data.partner_id.id or False,
				'channel_id': data.channel_id and data.channel_id.id or False,
				'categ_id': data.lead_categ_id and data.lead_categ_id.id or False,
				'type_id': data.type_id and data.type_id.id or False,
				'sel_contact_id': data.partner_contact_id and data.partner_contact_id.id or False,
				'type': 'lead',
				'lead_statut': 'running',
				'function': data.partner_contact_id and data.partner_contact_id.job_id and data.partner_contact_id.job_id.function,
				
			}
			if data.partner_contact_id:
				vals['title'] = data.partner_contact_id.title and data.partner_contact_id.title.id or False
				vals['contact_name'] = data.partner_contact_id.first_name and (data.partner_contact_id.first_name + ' ') + data.partner_contact_id.name
				addr = data.partner_contact_id.job_id and data.partner_contact_id.job_id.address_id or False
				if addr:
					if addr.partner_id:
						vals['partner_name'] = addr.partner_id.name
						vals['partner_id'] = addr.partner_id.id
					vals['email_from'] = addr.email
					if data.partner_contact_id.job_id.email:
						vals['email_from'] = data.partner_contact_id.job_id.email
					if data.partner_contact_id.email:
						vals['email_from'] = data.partner_contact_id.email
					vals['phone'] = addr.phone
					vals['fax'] = addr.fax
					vals['mobile'] = (data.partner_contact_id and data.partner_contact_id.mobile) or addr.mobile
					vals['street'] = addr.street
					vals['street2'] = addr.street2
					vals['zip'] = addr.zip
					vals['city'] = addr.city
					vals['country_id'] = addr.country_id and addr.country_id.id
					vals['state_id'] = addr.state_id and addr.state_id.id
			lead_id = lead_obj.create(cr, uid, vals)
		
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		

		act_win_id = act_obj.search( cr, uid, [('res_model','=','crm.lead'),('name','=','Leads')] )[0]
		act_win = act_obj.read(cr, uid, act_win_id, [], context=context)
		act_win['domain'] = eval(act_win['domain']) + [('id','=',lead_id)]
		act_win['name'] = _('Lead')
		act_win['context'] = "{'aptes_mode':True, 'search_default_current':1, 'default_type': 'lead', 'search_default_section_id': section_id, 'stage_type': 'lead' }"
		
		return act_win

crm_contact2lead()

