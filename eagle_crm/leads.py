# -*- coding: utf-8 -*-
#
#  File: crm_lead.py
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

from osv import osv,fields
import netsvc
import datetime
from tools.translate import _

class crm_lead(osv.osv):
	_inherit = 'crm.lead'
	
	_columns = {
		'sel_contact_id': fields.many2one('res.partner.contact', 'Contact',  domain="[('partner_id', '=', partner_id)]"),
		'partner_addresses': fields.one2many('res.partner.address', 'partner_id', 'Contacts'),
		'contacts_jobs': fields.one2many('res.partner.job', 'address_id', 'Jobs'),
		'lead_statut': fields.selection( [
			( 'running','Running' ),
			( 'late', 'Late' ),
			( 'old', 'Old' ), 
			] , 'Lead State'),
		'partner_ids': fields.many2many('res.partner', 'res_partners_leads_rel', 'child_id', 'parent_id', 'Partners Contacts'), 
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def onchange_partner_id(self, cr, uid, ids, part, email=False):
		ret = super(crm_lead,self).onchange_partner_id(cr, uid, ids, part, email=email)
		
		logger = netsvc.Logger()
		#logger.notifyChannel('Productivity/CRM - onchanger_partner_id', netsvc.LOG_INFO, " ret="+str(ret) )
		part_addr = []
		cnt_jobs = []
		contacts = []
		if ret['value']['partner_address_id']:
			partner = self.pool.get('res.partner').browse(cr, uid, part, context={})
			if partner:
				for pa in partner.address:
					part_addr.append(pa.id)
					for job in pa.job_ids:
						if job.id not in cnt_jobs:
							cnt_jobs.append(job.id)
							if job.contact_id and (job.contact_id.id not in contacts):
								contacts.append(job.contact_id.id)
		ret['value']['partner_addresses'] = part_addr
		ret['value']['contacts_jobs'] = cnt_jobs
		
		ret['value']['sel_contact_id'] = False
		contact = {
			'partner_name': False,
			'title': False,
			'function': False,
			'street': False,
			'street2': False,
			'zip': False,
			'city': False,
			'country_id': False,
			'state_id': False,
		}
		
		#logger.notifyChannel('Productivity/CRM - onchanger_partner_id', netsvc.LOG_INFO, " contacts="+str(contacts) )
		if len(contacts) == 1:
			contact_id = contacts[0]
			ret['value']['sel_contact_id'] = contact_id
			cr.execute( "Select min(sequence_partner), address_id from res_partner_job " + \
							"where address_id in (" + ','.join( map( lambda x: str(x), part_addr ) ) + ") " + \
							"and contact_id=" + str( contact_id ) + \
							" group by address_id" )
			row = cr.fetchone()
			if row and row[1]:
				addr_obj = self.pool.get('res.partner.address').read(cr, uid, row[1])
				if addr_obj:
					for fld in contact:
						if (fld in addr_obj) and addr_obj[fld]:
							contact[fld] = addr_obj[fld]
			contacts_names = self.pool.get('res.partner.contact').name_get(cr, uid, [contact_id])
			contact['partner_name'] = contacts_names[0][1]
		
		for fld in contact:
			ret['value'][fld] = contact[fld]
			
		return ret

	def onchange_contact_id(self, cr, uid, ids, part, cnt):
		ret = { 'value': {} }
		if not cnt or not part:
			return ret

		contact = {
			'partner_name': False,
			'title': False,
			'function': False,
			'street': False,
			'street2': False,
			'zip': False,
			'city': False,
			'country_id': False,
			'state_id': False,
		}
		contact_by_id = {
		}
		
		if cnt:
			cr.execute( "Select min(sequence_partner), address_id from res_partner_job " + \
							"where address_id in (select id from res_partner_address where partner_id=" + str(part) + ") " + \
							"and contact_id=" + str( cnt ) + \
							" group by address_id" )
			row = cr.fetchone()
			if row and row[1]:
				addr_obj = self.pool.get('res.partner.address').read(cr, uid, row[1])
				if addr_obj:
					for fld in contact:
						if (fld in addr_obj) and addr_obj[fld]:
							contact[fld] = addr_obj[fld]
			contacts_names = self.pool.get('res.partner.contact').name_get(cr, uid, [cnt])
			contact['partner_name'] = contacts_names[0][1]
			
		for fld in contact:
			ret['value'][fld] = contact[fld]
		for fld in contact_by_id:
			ret['value'][fld] = (contact_by_id[fld] and contact_by_id[fld].id) or False
			
		return ret

	def action_makeMeeting(self, cr, uid, ids, context=None):
		"""
		This opens Meeting's calendar view to schedule meeting on current Opportunity
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of Opportunity to Meeting IDs
		@param context: A standard dictionary for contextual values

		@return : Dictionary value for created Meeting view
		"""
		value = {}
		for opp in self.browse(cr, uid, ids, context=context):
			data_obj = self.pool.get('ir.model.data')

			# Get meeting views
			result = data_obj._get_id(cr, uid, 'crm', 'view_crm_case_meetings_filter')
			res = data_obj.read(cr, uid, result, ['res_id'])
			id1 = data_obj._get_id(cr, uid, 'crm', 'crm_case_calendar_view_meet')
			id2 = data_obj._get_id(cr, uid, 'crm', 'crm_case_form_view_meet')
			id3 = data_obj._get_id(cr, uid, 'crm', 'crm_case_tree_view_meet')
			if id1:
				id1 = data_obj.browse(cr, uid, id1, context=context).res_id
			if id2:
				id2 = data_obj.browse(cr, uid, id2, context=context).res_id
			if id3:
				id3 = data_obj.browse(cr, uid, id3, context=context).res_id

			context = {
				'default_opportunity_id': opp.id,
				'default_partner_id': opp.partner_id and opp.partner_id.id or False,
				'default_user_id': uid, 
				'default_section_id': opp.section_id and opp.section_id.id or False,
				'default_email_from': opp.email_from,
				'default_state': 'open',  
				'default_name': opp.name,
				'default_contract_id': opp.contract_id and opp.contract_id.id or False,
				'default_contact_id': opp.sel_contact_id and opp.sel_contact_id.id or False,
			}
			value = {
				'name': _('Meetings'),
				'context': context,
				'view_type': 'form',
				'view_mode': 'calendar,form,tree',
				'res_model': 'crm.meeting',
				'view_id': False,
				'views': [(id1, 'calendar'), (id2, 'form'), (id3, 'tree')],
				'type': 'ir.actions.act_window',
				'search_view_id': res['res_id'],
				'nodestroy': True
			}
		return value

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		res = []
		for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street']):
			addr = r['name'] or ''
			res.append((r['id'], addr.strip() or '?'))
		return res

crm_lead()
