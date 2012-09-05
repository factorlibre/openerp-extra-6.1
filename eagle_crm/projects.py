# -*- coding: utf-8 -*-
#
#  File: projects.py
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

import netsvc
from osv import fields, osv
import tools
from tools.translate import _

class project_issue(osv.osv):
	_inherit = "project.issue"

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def create( self, cr, uid, vals, context=None ):
		projects = self.pool.get( 'project.project' )
		if 'project_id' in vals:
			if vals['project_id']:
				prj = projects.browse( cr, uid, vals['project_id'], context=context )
				if prj:
					if hasattr(prj, 'contract_id') and prj.contract_id:
						proj_ids = projects.search( cr, uid, [('contract_id','=',prj.contract_id.id)], context=context )
						if proj_ids and len( proj_ids ):
							vals['project_id'] =  proj_ids[0]
						vals['contract_id'] = prj.contract_id.id
		return super( project_issue, self ).create( cr, uid, vals, context=context )				
	
project_issue()
