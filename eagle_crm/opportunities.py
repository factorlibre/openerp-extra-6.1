# -*- coding: utf-8 -*-
#
#  File: opportunities.py
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
import netsvc
import datetime
from tools.translate import _

class crm_opportunity(osv.osv):
	_inherit = 'crm.lead'
	
	def conditional_close_contract( self, cr, uid, contract_ids ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) called" )
		if not contract_ids:
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) cancelled by 1" )
			return False
		if not len(contract_ids):
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) cancelled by 2" )
			return False

		ret = False
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		for contract in self.pool.get( 'eagle.contract' ).browse( cr, uid, contract_ids, context=context ):
			close_it = True
			open_it = True
			for opp in contract.opportunity_ids:
				if opp.probability > 0.0:
					close_it = False
				if opp.probability == 0.0:
					open_it = False

			if close_it:
				if not open_it:
					self.pool.get( 'eagle.contract' ).contract_close( cr, uid, contract.id, context=context )
					ret = True 
			elif open_it:
				self.pool.get( 'eagle.contract' ).contract_installation( cr, uid, contract.id, context=context )
				ret = True 

		return ret

	def eagle_crm_case_close(self, cr, uid, ids, *args):
		"""Overrides close for crm_case for setting probability and close date
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of case Ids
		@param *args: Tuple Value for additional Params
		"""
		res = self._case_close_generic(cr, uid, ids, self._find_won_stage, *args)
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }

		contracts_to_check = []		
		for (id, name) in self.name_get(cr, uid, ids):
			opp = self.browse(cr, uid, id)
			if opp.type == 'opportunity':
				message = _("The opportunity '%s' has been won.") % name
				if opp.contract_id:
					ret = contracts_to_check.append(opp.contract_id.id)
					if ret: 
						message += _("The contract '%s'has been set to Production") % opp.contract_id.name
				self.log(cr, uid, id, message)
		
		if len(contracts_to_check):
			self.conditional_close_contract( cr, uid, contracts_to_check )
		return res

	def eagle_crm_case_mark_lost(self, cr, uid, ids, *args):
		"""Mark the case as lost: state = done and probability = 0%
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of case Ids
		@param *args: Tuple Value for additional Params
		"""
		res = self._case_close_generic(cr, uid, ids, self._find_lost_stage, *args)
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		
		contracts_to_check = []		
		for (id, name) in self.name_get(cr, uid, ids):
			opp = self.browse(cr, uid, id)
			if opp.type == 'opportunity':
				message = _("The opportunity '%s' has been marked as lost.") % name
				if opp.contract_id:
					ret = contracts_to_check.append(opp.contract_id.id)
					if ret: 
						message += _("The contract '%s'has been set to Production") % opp.contract_id.name
				self.log(cr, uid, id, message)
		
		if len(contracts_to_check):
			self.conditional_close_contract( cr, uid, contracts_to_check )
		return res

crm_opportunity()
