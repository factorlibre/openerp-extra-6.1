# -*- coding: utf-8 -*-
#
#  File: inits.py
#  Module: ons_multicompany_views
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc
from osv import fields, osv

class opennet_own_inits(osv.osv):
	_name = 'opennet.own_inits'
	_description = 'opennet.own_inits'
	
	def __init__(self, pool, cr):
		super(opennet_own_inits, self).__init__(pool, cr)
		
		cr.execute("Select id from ir_model where model='product.template'")
		row = cr.fetchone()
		if row and row[0]:
			model_id = row[0]
			q = "Update ir_rule set domain_force=%s where model_id=%s and domain_force=%s"
			p = ( "['|','|',('company_id','=',False),('company_id','child_of',[user.company_id.id]),('ons_companies','in',[user.company_id.id])]",
					model_id, "['|',('company_id','=',False),('company_id','child_of',[user.company_id.id])]" )
			cr.execute( q, p )

		# 2010-03-17/Cyp: new: same for res.partner objects
		cr.execute("Select id from ir_model where model='res.partner'")
		row = cr.fetchone()
		if row and row[0]:
			model_id = row[0]

			# Not sure about the future: conditions are inverted, compared to the products
			# so that the query is done twice, with both cases
			q = "Update ir_rule set domain_force=%s where model_id=%s and domain_force=%s"
			p = ( "['|','|', ('company_id','child_of',[user.company_id.id]),('company_id','=',False),('ons_companies','in',[user.company_id.id])]",
					model_id, "['|', ('company_id','child_of',[user.company_id.id]),('company_id','=',False)]" )
			cr.execute( q, p )


			q = "Update ir_rule set domain_force=%s where model_id=%s and domain_force=%s"
			p = ( "['|','|', ('company_id','=',False),('company_id','child_of',[user.company_id.id]),('ons_companies','in',[user.company_id.id])]",
					model_id, "['|', ('company_id','=',False),('company_id','child_of',[user.company_id.id])]" )
			cr.execute( q, p )

opennet_own_inits()
