# -*- coding: utf-8 -*-
#
#  File: analytics.py
#  Module: eagle_project
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

class analytic_account(osv.osv):
	_inherit = "account.analytic.line"

	def create( self, cr, uid, vals, context=None ):
		if not vals.get( 'to_invoice', False ):
			cr.execute( """Select c.ons_hrtif_to_invoice 
				From eagle_contract c, project_project p 
				Where c.id=p.contract_id 
				And p.analytic_account_id="""+str(vals['account_id']) )
			row = cr.fetchone()
			if row and row[0]:
				vals['to_invoice'] = row[0]
		
		return super( analytic_account, self ).create( cr, uid, vals, context=context )

	def write(self, cr, uid, ids, vals, context=None):
		if not vals:
			return True
		if  vals.get( 'account_id', False ) and not vals.get( 'to_invoice', False ):
			cr.execute( """Select c.ons_hrtif_to_invoice 
				From eagle_contract c, project_project p 
				Where c.id=p.contract_id 
				And p.analytic_account_id="""+str(vals['account_id']) )
			row = cr.fetchone()
			if row and row[0]:
				vals['to_invoice'] = row[0]

		return super( analytic_account, self ).write( cr, uid, ids, vals, context=context )

analytic_account()

class hr_timesheet_line(osv.osv):
	_inherit = "hr.analytic.timesheet"

	def create(self, cr, uid, vals, *args, **kwargs):
		return super(hr_timesheet_line,self).create(cr, uid, vals, *args, **kwargs)

hr_timesheet_line()
