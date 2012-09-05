# -*- coding: utf-8 -*-
#
#  File: projects.py
#  Module: eagle_project
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
import tools
from tools.translate import _

class task(osv.osv):
	_inherit = "project.task"

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}

	def create( self, cr, uid, vals, context=None ):
		projects = self.pool.get( 'project.project' )
		if 'project_id' in vals:
			if vals['project_id']:
				prj = projects.browse( cr, uid, vals['project_id'], context=context )
				if prj:
					if prj.contract_id:
						#proj_use = prj.contract_id.state == 'opened' and 'inst' or 'maint'
						proj_use = prj.contract_id.state == 'installation' and 'inst' or 'maint'
						#proj_ids = projects.search( cr, uid, [('parent_id','=',prj.contract_id.project_id.id),('project_use','=',proj_use)], context=context )
						proj_ids = projects.search( cr, uid, [('contract_id','=',prj.contract_id.id),('project_use','=',proj_use)], context=context )
						if proj_ids and len( proj_ids ):
							vals['project_id'] =  proj_ids[0]
						vals['contract_id'] = prj.contract_id.id
					if 'user_id' not in vals:
						vals['user_id'] = False
					if not vals['user_id']:
						vals['user_id'] = prj.user_id and prj.user_id.id or False
		if 'procurement_id' in vals:
			if vals['procurement_id']:
				pro = self.pool.get( 'procurement.order' ).browse( cr, uid, vals['procurement_id'], context=context )
				if pro and pro.product_id and pro.product_id.product_manager:
					vals['user_id'] = pro.product_id.product_manager.id
		return super( task, self ).create( cr, uid, vals, context=context )

task()

class project(osv.osv):
	_inherit = "project.project"

	def _retrieve_parent_project( self, cr, uid, prj_ids, name, args, context ):
		res = {}
		aaa_tbl = self.pool.get( 'account.analytic.account' )
		for prj in self.browse( cr, uid, prj_ids, context=context ):
			res[prj.id] = False
			aaa_parent = prj.parent_id	# 
			if aaa_parent and aaa_parent.id:
				cr.execute("Select id from project_project where analytic_account_id=" + str(aaa_parent.id) )
				row = cr.fetchone()
				if row and len( row ) > 0:
					res[prj.id] = row[0]
		
		return res

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'project_use': fields.selection( [
				( 'grouping','Grouping' ),
				( 'inst','Installation' ),
				( 'maint','Maintenance' ),
				], 'Project Use' ),
		'parent_project': fields.function( _retrieve_parent_project, method=True, string="Parent Project", type="many2one", relation="project.project" ),
	}

	def create( self, cr, uid, vals, context=None ):
		contract_id = False
		if 'contract_id' in vals:
			contract_id = vals['contract_id']
		if not contract_id:
			analytic_account_id = False
			if 'analytic_account_id' in vals:
				analytic_account_id = vals['analytic_account_id']
			if analytic_account_id:
				cr.execute( "Select parent_id from account_analytic_account Where id=%d" % analytic_account_id )
				row = cr.fetchone()
				if row and len( row ) > 0:
					cr.execute( "Select contract_id from project_project Where analytic_account_id=%d" % row[0] )
					row = cr.fetchone()
					if row and len( row ) > 0:
						contract_id = row[0]
		if contract_id:
			vals['contract_id'] = contract_id
		return super( project, self ).create( cr, uid, vals, context=context )

project()

class project_work( osv.osv ):
	_inherit = 'project.task.work'

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'ons_hrtif_to_invoice': fields.many2one('hr_timesheet_invoice.factor', 'Reinvoice Costs', required=True, 
			help="Fill this field if you plan to automatically generate invoices based " \
			"on the costs in this analytic account: timesheets, expenses, ..." \
			"You can configure an automatic invoice rate on analytic accounts."),
		'ons_hrtif_why_chg': fields.char('Why change the factor', size=60),
		'ons_hrtif_changed': fields.boolean('Change the factor?'),
	}

	def _default_hrtif_id(self, cr, uid, context=None):
		cr.execute( "select id from hr_timesheet_invoice_factor order by factor asc limit 1" )
		row = cr.fetchone()
		ret = False
		if row and row[0]:
			ret = row[0]
		
		return ret

	_defaults = {
		'ons_hrtif_to_invoice': _default_hrtif_id,
	}

	def create(self, cr, uid, vals, *args, **kwargs):
		context = kwargs.get('context', {})
		if not context.get('no_analytic_entry',False):
			if 'task_id' in vals:
				task = self.pool.get('project.task').browse(cr, uid, vals['task_id'], context=context)
				if task:
					contract_id = task and task.contract_id and task.contract_id.id or False
					if contract_id:
						vals.update({'contract_id': contract_id})
		
		return super(project_work,self).create(cr, uid, vals, *args, **kwargs)

	def create_nada_2(self, cr, uid, vals, *args, **kwargs):
		work_id = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
		if not work_id: return False
		
		context = kwargs.get('context', {})
		if not context.get('no_analytic_entry',False):
			work = self.browse(cr, uid, work_id, context=context)
			if not work: return False
	
			timeline = work.hr_analytic_timesheet_id
			if timeline and work.hr_analytic_timesheet_id:
				contract_id = work.task_id and work.task_id.contract_id and work.task_id.contract_id.id or False
				if contract_id:
					self.pool.get('hr.analytic.timesheet').write(cr, uid, [work.hr_analytic_timesheet_id.id], {'contract_id':contract_id}, context)
		
		return work_id

	def button_change_hrtif_yes(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'ons_hrtif_changed':True} )
		return True

	def button_change_hrtif_no(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'ons_hrtif_changed':False} )
		return True


project_work()
