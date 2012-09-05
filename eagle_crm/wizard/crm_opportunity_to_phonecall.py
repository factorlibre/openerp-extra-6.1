# -*- coding: utf-8 -*-
#
#  File: wizard/crm_opportunity_to_phonecall.py
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

class crm_opportunity_to_phonecall(osv.osv_memory):

	_inherit = 'crm.opportunity2phonecall'

	
	def action_apply(self, cr, uid, ids, context=None):
		"""
		This converts Opportunity to Phonecall and opens Phonecall view
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user's ID for security checks,
		@param ids: List of Opportunity to Phonecall IDs
		@param context: A standard dictionary for contextual values

		@return : Dictionary value for created Opportunity form
		"""
		value = {}
		record_ids = context and context.get('active_ids', []) or []

		phonecall_obj = self.pool.get('crm.phonecall')
		opp_obj = self.pool.get('crm.lead')
		mod_obj = self.pool.get('ir.model.data')
		result = mod_obj._get_id(cr, uid, 'crm', 'view_crm_case_phonecalls_filter')
		res = mod_obj.read(cr, uid, result, ['res_id'])

		data_obj = self.pool.get('ir.model.data')

		# Select the view
		id2 = data_obj._get_id(cr, uid, 'crm', 'crm_case_phone_tree_view')
		id3 = data_obj._get_id(cr, uid, 'crm', 'crm_case_phone_form_view')
		if id2:
			id2 = data_obj.browse(cr, uid, id2, context=context).res_id
		if id3:
			id3 = data_obj.browse(cr, uid, id3, context=context).res_id

		for this in self.browse(cr, uid, ids, context=context):
			for opp in opp_obj.browse(cr, uid, record_ids, context=context):
				addr = False
				if opp.partner_address_id:
					addr = opp.partner_address_id.id
				if not addr:
					if opp.sel_contact_id and opp.sel_contact_id.job_id and opp.sel_contact_id.job_id.address_id:
						addr = opp.sel_contact_id.job_id.address_id.id
				new_case = phonecall_obj.create(cr, uid, {
						'name' : this.name,
						'case_id' : opp.id ,
						'user_id' : this.user_id and this.user_id.id or False,
						'categ_id' : this.categ_id.id,
						'description' : opp.description or False,
						'date' : this.date,
						'section_id' : this.section_id.id or opp.section_id.id or False,
						'partner_id': opp.partner_id and opp.partner_id.id or False,
						'partner_address_id': addr,
						'partner_phone' : opp.phone or (opp.partner_address_id and opp.partner_address_id.phone or False),
						'partner_mobile' : (opp.sel_contact_id and opp.sel_contact_id.mobile) or (opp.partner_address_id and opp.partner_address_id.mobile) or False,
						'priority': opp.priority,
						'opportunity_id': opp.id,
						'contract_id': opp.contract_id and opp.contract_id.id,
						'partner_addr_contact': opp.sel_contact_id and opp.sel_contact_id.id or False,
				}, context=context)

				phonecall_obj.case_open(cr, uid, [new_case])

			value = {
				'name': 'Phone Call',
				'domain': "[('user_id','=',%s),('opportunity_id','=',%s)]" % (uid,opp.id),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'crm.phonecall',
				'res_id' : new_case,
				'views': [(id3, 'form'), (id2, 'tree'), (False, 'calendar')],
				'type': 'ir.actions.act_window',
				'search_view_id': res['res_id']
			}
		return value
	
crm_opportunity_to_phonecall()
