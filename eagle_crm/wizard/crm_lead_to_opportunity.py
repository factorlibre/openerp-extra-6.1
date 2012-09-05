# -*- coding: utf-8 -*-
#
#  File: wizard/crm_lead_to_opportunity.py
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
from tools.translate import _


class crm_lead2opportunity(osv.osv_memory):
	_inherit = 'crm.lead2opportunity'

	def action_apply(self, cr, uid, ids, context=None):
		"""
		This converts lead to opportunity and opens Opportunity view
		@param ids: ids of the leads to convert to opportunities

		@return : View dictionary opening the Opportunity form view
		"""
		record_id = context and context.get('active_id') or False
		if not record_id:
			return {'type': 'ir.actions.act_window_close'}

		leads = self.pool.get('crm.lead')
		models_data = self.pool.get('ir.model.data')
		calls = self.pool.get('crm.phonecall')
		meetings = self.pool.get('crm.meeting')

		# Get Opportunity views
		result = models_data._get_id(
			cr, uid, 'crm', 'view_crm_case_opportunities_filter')
		opportunity_view_search = models_data.browse(
			cr, uid, result, context=context).res_id
		opportunity_view_form = models_data._get_id(
			cr, uid, 'crm', 'crm_case_form_view_oppor')
		opportunity_view_tree = models_data._get_id(
			cr, uid, 'crm', 'crm_case_tree_view_oppor')
		if opportunity_view_form:
			opportunity_view_form = models_data.browse(
				cr, uid, opportunity_view_form, context=context).res_id
		if opportunity_view_tree:
			opportunity_view_tree = models_data.browse(
				cr, uid, opportunity_view_tree, context=context).res_id

		lead = leads.browse(cr, uid, record_id, context=context)
		stage_ids = self.pool.get('crm.case.stage').search(cr, uid, [('type','=','opportunity'),('sequence','>=',1)])
		contract_obj = self.pool.get('eagle.contract')
		
		for this in self.browse(cr, uid, ids, context=context):
			vals = {
				'name': this.name,
				'customer_id': this.partner_id.id,
				'opportunity_id': lead.id,
			}
			if this.partner_id.property_product_pricelist:
				vals['pricelist_id'] = this.partner_id.property_product_pricelist.id
			contract_id = contract_obj.create(cr, uid, vals, context=context)
			
			call = calls.search( cr, uid, [('opportunity_id','=',lead.id)], context=context )
			if call:
				calls.write(cr, uid, call, {'contract_id':contract_id})
			meeting = meetings.search( cr, uid, [('opportunity_id','=',lead.id)], context=context )
			if meeting:
				meetings.write(cr, uid, meeting, {'contract_id':contract_id}, context=context)
			
			vals ={
				'planned_revenue': this.planned_revenue,
				'probability': this.probability,
				'name': this.name,
				'partner_id': this.partner_id.id,
				'user_id': (this.partner_id.user_id and this.partner_id.user_id.id) or (lead.user_id and lead.user_id.id),
				'type': 'opportunity',
				'stage_id': stage_ids and stage_ids[0] or False,
				'contract_id': contract_id,
			}
			if not lead.partner_address_id:
				if lead.sel_contact_id and lead.sel_contact_id.job_id and lead.sel_contact_id.job_id.address_id:
					vals['partner_address_id'] =  lead.sel_contact_id.job_id.address_id.id
			lead.write(vals, context=context)
			leads.history(cr, uid, [lead], _('Opportunity'), details='Converted to Opportunity', context=context)
			if lead.partner_id:
				msg_ids = [ x.id for x in lead.message_ids]
				self.pool.get('mailgate.message').write(cr, uid, msg_ids, {
					'partner_id': lead.partner_id.id
				}, context=context)
			
			leads.log(cr, uid, lead.id,
				_("Lead '%s' has been converted to an opportunity.") % lead.name)

		return {
			'name': _('Opportunity'),
			'view_type': 'form',
			'view_mode': 'form,tree',
			'res_model': 'crm.lead',
			'domain': [('type', '=', 'opportunity')],
			'res_id': int(lead.id),
			'view_id': False,
			'views': [(opportunity_view_form, 'form'),
					  (opportunity_view_tree, 'tree'),
					  (False, 'calendar'), (False, 'graph')],
			'type': 'ir.actions.act_window',
			'search_view_id': opportunity_view_search
		}

	_columns = {
		'name' : fields.char('Opportunity', size=64, required=True, select=1),
		'probability': fields.float('Success Rate (%)'),
		'planned_revenue': fields.float('Expected Revenue'),
		'partner_id': fields.many2one('res.partner', 'Partner'),
		'contract_id': fields.many2one('eagle.contract', 'Contract'),
	}
	
crm_lead2opportunity()
