# -*- coding: utf-8 -*-
#
#  File: crm_phonecall.py
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

from osv import osv,fields

class crm_phonecall(osv.osv):
	_inherit = 'crm.phonecall'
	
	_columns = {
        'partner_contact': fields.related('partner_address_id', 'name', \
                                 type="char", string="Address", size=128), 
        'partner_addr_contact': fields.many2one( 'res.partner.contact', 'Contact', domain="[('partner_id','=',partner_id)]" ),
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
	}
	
	def create( self, cr, uid, vals, context=None ):
		opps = self.pool.get( 'crm.lead' )
		if 'opportunity_id' in vals:
			if vals['opportunity_id']:
				opp = opps.browse( cr, uid, vals['opportunity_id'], context=context )
				if opp:
					if opp.contract_id:
						opp_ids = opps.search( cr, uid, [('contract_id','=',opp.contract_id.id)], context=context )
						if opp_ids and len( opp_ids ):
							vals['opportunity_id'] =  opp_ids[0]
						vals['contract_id'] = opp.contract_id.id
					
		return super( crm_phonecall, self ).create( cr, uid, vals, context=context )
		
	defaults = {
        'contract_id': lambda s,cr,uid,context: context and context.get('default_contract_id', False) or False,
	}

crm_phonecall()
