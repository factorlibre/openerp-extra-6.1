# -*- coding: utf-8 -*-
#
#  File: wizard/new_contact_for_partner.py
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

class new_contact_for_partner(osv.osv_memory):
	"""Create a contact for a partner"""
	
	_name = 'eagle.contact4partner'
	_description = 'Contact for a Partner'

	_columns = {
		'name': fields.char('Last Name', size=64, required=True),
		'first_name': fields.char('First Name', size=64),
		'mobile': fields.char('Mobile', size=64),
		'title': fields.many2one('res.partner.title','Title'),
		'website': fields.char('Website', size=120),
		'lang_id': fields.many2one('res.lang', 'Language'),
		'country_id': fields.many2one('res.country','Nationality'),
		'birthdate': fields.date('Birth Date'),
		'active': fields.boolean('Active', help="If the active field is set to true,\
				 it will allow you to hide the partner contact without removing it."),
		'email': fields.char('E-Mail', size=240),
		'comment': fields.text('Notes', translate=True),
		'photo': fields.binary('Image'),
		'function': fields.char("Contact's function at this address", size=50),
		'seq': fields.integer('Contact sequence number'),

	}
	_defaults = {
		'active' : lambda *a: True,
	}
	
	def make_contact(self, cr, uid, ids, context=None):
		"""
		This function creates a new contact.
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of IDs
		@param context: A standard dictionary for contextual values
		
		@return : an empty dictionary.
		"""
		if not context:
			context = {}
		
		contact_obj = self.pool.get('res.partner.contact')
		job_obj = self.pool.get('res.partner.job')
		
		for data in self.browse(cr, uid, ids):
			contact_id = contact_obj.create(cr, uid, {
					'name': data.name,
					'first_name': data.first_name,
					'mobile': data.mobile,
					'title': (data.title and data.title.id) or False,
					'website': data.website,
					'lang_id': (data.lang_id and data.lang_id.id) or False,
					'country_id': (data.country_id and data.country_id.id) or False,
					'birthdate': data.birthdate,
					'active': data.active,
					'email': data.email,
					'comment': data.comment,
					'photo': data.photo,
				})
			job_id = job_obj.create(cr, uid, {
				'address_id': context['active_id'],
				'contact_id': contact_id,
				'function': data.function,
				'sequence_contact': data.seq,
				'email': data.email,
				'phone': data.mobile,
			})
		
		return {}

new_contact_for_partner()
