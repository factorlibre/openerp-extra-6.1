# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_products_2_contracts.py
#  Module: ons_contracts
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#
# Author Yvon Philiippe Crittin / Open Net Sarl
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard,osv,pooler

class wiz_products_2_contracts(wizard.interface):

	def _action_idle(self, cr, uid, data, context):
		return { }

	def _action_open_contracts_list(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		
		title = 'Corresponding contracts'
		domain = False

		cr.execute( "Select contract_id From eagle_contract_position Where name="+str(context['active_id']) )
		rows = cr.fetchall()
		if rows and len( rows ):
			domain = [('id','in',[ x[0] for x in rows ])]
			
		res = {
			'domain': str(domain),
			'name': title,
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'eagle.contract',
			'view_id': False,
			'type': 'ir.actions.act_window'
		}

		return res

	states = {
		'init': {
			'actions': [],
			'result': {'type':'action', 'action':_action_idle, 'state':'next'}
		},
		'next': {
			'actions': [],
			'result': {'type':'action', 'action':_action_open_contracts_list, 'state':'end'}
		},
	}

wiz_products_2_contracts('eagle_wizard_products_2_contracts')
