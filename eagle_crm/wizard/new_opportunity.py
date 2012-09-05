# -*- coding: utf-8 -*-
#
#  File: wizard/new_opportunity.py
#  Module: eagle_crm
#
#  Created by sbe@open-net.ch
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
import time
import crm
from datetime import datetime, timedelta, date
from tools.translate import _

class new_opportunity(osv.osv_memory):
	"""Create a new opportunity"""
	
	_name = 'eagle.wizard.new_opportunity'
	_description = 'New opportunity'

	_columns = {
		'name': fields.char('Last Name', size=64, required=True),
		'description': fields.text('Notes'),
		'partner_id': fields.many2one('res.partner', 'Partner Contact'),
		'partner_ids': fields.many2many('res.partner', 'res_partners_leads_rel', 'uid', 'pid', 'Partner Contact'),
		'partner_contact_id': fields.many2one('res.partner.contact', 'Partner Contact', domain="[('partner_id','=',partner_id)]"),
		'user_id': fields.many2one('res.users', 'Salesman'),
		'type':fields.selection([('lead','Lead'),('opportunity','Opportunity'),],'Type', help="Type is used to separate Leads and Opportunities"),
		'probability': fields.float('Probability (%)',group_operator="avg"),
		'planned_revenue': fields.float('Expected Revenue'),
		'date_deadline': fields.date('Expected Closing'),
		'priority': fields.selection([('1', 'Highest'),('2', 'High'),('3', 'Normal'),('4', 'Low'),('5', 'Lowest'),], 'Priority'),
		'section_id': fields.many2one('crm.case.section', 'Sales Team'),
		'state':fields.selection([('step1','step1'),('step2','step2'),('step3','step3'),('step4','step4'),('step5','step5'),('step6','step6')], 'states', readonly=True),
		'meeting_name': fields.char('Summary', size=124), 
		'date_meeting': fields.datetime('Date'),
		'date_deadline': fields.datetime('Deadline'),
		'meeting_description': fields.text('Notes'),
		'categ_id': fields.many2one('crm.case.categ', 'Meeting Type', domain="[('object_id.model', '=', 'crm.meeting')]"),
		'duration': fields.datetime('Duration'),
		'alarm_id': fields.many2one('res.alarm','Alarm'),
		'location': fields.char('Location', size=32),
		'call_name': fields.char('Summary', size=124),
		'categ_call_id': fields.many2one('crm.case.categ', 'Category', domain="['|',('section_id','=',section_id),('section_id','=',False),\
						('object_id.model', '=', 'crm.phonecall')]"), 
		'partner_phone': fields.char('Phone', size=32),  
		'partner_mobile': fields.char('Mobile', size=32),
		'date_call': fields.datetime('Date'), 
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'lead_statut': fields.selection([('running','Running'),('late','Late'),('old','Old')],'State', readonly=True),
	}
	_defaults = {
		'state': 'step1',
		'name': lambda *a: _('New Opportunity'),
		'meeting_name': lambda *a: _('New Meeting'),
		'call_name': lambda *a: _('New Call'),
		'user_id': lambda self, cr, uid, ctx: uid,
		'type': lambda *a: 'opportunity',
		'date_meeting': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'date_deadline': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'date_call': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'lead_statut': lambda *a: 'running',
	}
	
	def onchange_dates(self, cr, uid, ids, start_date, duration=False, end_date=False, allday=False, context=None):
		"""Returns duration and/or end date based on values passed
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of calendar event’s IDs.
		@param start_date: Starting date
		@param duration: Duration between start date and end date
		@param end_date: Ending Datee
		@param context: A standard dictionary for contextual values
		"""
		if context is None:
			context = {}

		value = {}
		if not start_date:
			return value
		if not end_date and not duration:
			duration = 1.00
			value['duration'] = duration

		if allday: # For all day event
			value = {'duration': 24}
			duration = 24.0

		start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
		if end_date and not duration:
			end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			value['duration'] = round(duration, 2)
		elif not end_date:
			end = start + timedelta(hours=duration)
			value['date_deadline'] = end.strftime("%Y-%m-%d %H:%M:%S")
		elif end_date and duration and not allday:
			# we have both, keep them synchronized:
			# set duration based on end_date (arbitrary decision: this avoid 
			# getting dates like 06:31:48 instead of 06:32:00)
			end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			value['duration'] = round(duration, 2)

		return {'value': value}
	
	def go_step1(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step1'}, context=context)
		return True
	
	def go_step2(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step2'}, context=context)
		return True
	
	def go_step3(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step3'}, context=context)
		return True
	
	def go_step4(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step4'}, context=context)
		return True
		
	def go_step5(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step5'}, context=context)
		return True

	def go_step6(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'step6'}, context=context)
		return True

	
	def make_opportunity(self, cr, uid, ids, context=None):
		
		if not context:
			context = {}
		
		lead_obj = self.pool.get('crm.lead')
		meeting_obj = self.pool.get('crm.meeting')
		call_obj = self.pool.get('crm.phonecall')
		contract_obj = self.pool.get('eagle.contract')
		
		for data in self.browse(cr, uid, ids):
		
			addr = False
			contract_id = False
			if data.name != False:
				if not data.contract_id :
					contract_id = contract_obj.create(cr, uid, {
						'name': data.name,
						'customer_id': data.partner_id.id,
					})
				else:
					#recuperation du partner par rapport au contract... à faire...
					contract_id = data.contract_id.id
		
			vals = {
				'name': data.name,
				'description': data.description,
				'user_id': uid,
				'priority': data.priority,
				'date_deadline': data.date_deadline,
				'section_id': data.section_id and data.section_id.id or False,
				'planned_revenue': data.planned_revenue,
				'probability': data.probability,
				'partner_id': data.partner_id and data.partner_id.id or False,
				'partner_ids': [(6,0, [x.id for x in data.partner_ids])],
				'sel_contact_id': data.partner_contact_id and data.partner_contact_id.id or False,
				'type': 'opportunity',
				'contract_id': contract_id,
				'lead_statut': 'running',
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
					vals['mobile'] = addr.mobile
					vals['street'] = addr.street
					vals['street2'] = addr.street2
					vals['zip'] = addr.zip
					vals['city'] = addr.city
					vals['country_id'] = addr.country_id and addr.country_id.id
					vals['state_id'] = addr.state_id and addr.state_id.id
					vals['partner_address_id'] = addr.id
			opportunity_id = lead_obj.create( cr, uid, vals, context=context )
			contract_obj.write(cr, uid, contract_id,{'opportunity_id':opportunity_id})
				
			if not opportunity_id:
				raise osv.except_osv( 'Error!', 'Could not create the opportunity' )
			
			if data.state == 'step4' and data.meeting_name != False:
				meeting_id = meeting_obj.create(cr, uid, {
					'name': data.meeting_name,
					'categ_id': data.categ_id.id and data.categ_id.id or False,
					'partner_id': data.partner_id.id and data.partner_id.id or False,
					'partner_address_id': addr and addr.id or False,
					'email_from': 'email_from' in vals and vals['email_from'] or False,
					'categ_id': data.categ_call_id.id,
					'date_deadline': data.date_deadline,
					'date': data.date_meeting,
					'duration': data.duration,
					'location': data.location,
					'alarm_id': data.alarm_id and data.alarm_id.id or False,
					'opportunity_id': opportunity_id,
					'section_id': data.section_id and data.section_id.id or False,
					'contract_id': data.contract_id and data.contract_id.id or contract_id,
					'contact_id': data.partner_contact_id and data.partner_contact_id.id or False,
				})
				#contract_obj.write(cr, uid, contract_id,{'meetings':meeting_id})
				

			if data.state == 'step5' and data.call_name != False:
				call_id = call_obj.create(cr, uid, {
					'name': data.call_name,
					'partner_id': data.partner_id and data.partner_id.id or False,
					'partner_address_id': addr and addr.id or False,
					'user_id': uid,
					'date': data.date_call,
					'partner_phone': data.partner_phone,
					'partner_mobile': data.partner_mobile,
					'opportunity_id': opportunity_id,
					'categ_id': data.categ_call_id.id,
					'section_id': data.section_id and data.section_id.id or False,
					'priority': data.priority,
					'partner_addr_contact': data.partner_contact_id and data.partner_contact_id.id or False,
					'contract_id': data.contract_id and data.contract_id.id or contract_id,
				})
				#contract_obj.write(cr, uid, contract_id,{'phonecall_id':call_id})

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		
		act_win_id = act_obj.search( cr, uid, [('res_model','=','crm.lead'),('name','=','Opportunities')] )[0]
		act_win = act_obj.read(cr, uid, act_win_id, [], context=context)
		act_win['domain'] = eval(act_win['domain']) + [('id','=',opportunity_id)]
		act_win['name'] = _('Opportunity')
		act_win['context'] = "{'aptes_mode':True, 'search_default_current':1, 'default_type': 'opportunity', 'search_default_section_id': section_id, 'stage_type': 'opportunity' }"
		
		
		return act_win

new_opportunity()
