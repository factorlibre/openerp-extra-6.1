# -*- coding: utf-8 -*-
#
#  File: procurements.py
#  Module: eagle_contracts
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


class procurement_order( osv.osv ):
	_inherit = 'procurement.order'
	
	def create(self, cr, uid, vals, context=None):
		print " ***** vals=", vals
		return super( procurement_order, self ).create(cr, uid, vals, context=context)
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def action_produce_assign_service(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		for procurement in self.browse(cr, uid, ids):
			self.write(cr, uid, [procurement.id], {'state': 'running'})
			planned_hours = procurement.product_qty
			project_id = False
			if procurement.product_id.project_id:
				project_id = procurement.product_id.project_id.id
			if procurement.contract_id:
				if procurement.contract_id.project_id:
					project_id = procurement.contract_id.project_id.id
			task_id = self.pool.get('project.task').create(cr, uid, {
				'name': '%s:%s' % (procurement.origin or '', procurement.name),
				'date_deadline': procurement.date_planned,
				'planned_hours':planned_hours,
				'remaining_hours': planned_hours,
				'user_id': procurement.product_id.product_manager.id,
				'notes': procurement.note,
				'procurement_id': procurement.id,
				'description': procurement.note,
				'date_deadline': procurement.date_planned,
				'project_id': project_id,
				'state': 'draft',
				'company_id': procurement.company_id.id,
			},context=context)
			self.write(cr, uid, [procurement.id],{'task_id':task_id}) 
		return task_id

	def make_po(self, cr, uid, ids, context=None):
		res = super( procurement_order , self).make_po(cr, uid, ids, context=context) 
		purchases = self.pool.get( 'purchase.order' )
		if res and len(res):
			for proc_id in res:
				proc = self.browse( cr, uid, proc_id, context=context )
				if proc.contract_id and proc.purchase_id:
					purchases.write( cr, uid, proc.purchase_id.id, { 'contract_id': proc.contract_id.id } ) 
		return res

procurement_order()

