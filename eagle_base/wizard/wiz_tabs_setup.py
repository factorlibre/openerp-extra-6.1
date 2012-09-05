# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_tabs_setup.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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
from tools.misc import UpdateableStr, UpdateableDict
from tools.translate import _
import netsvc

VAR_FORM = UpdateableStr()
VAR_FIELDS = UpdateableDict()
VAR_FORM.string = u"""<?xml version="1.0"?>
<form string="Incompatible application">
<separator string="The wizard will close immediately" colspan="4"/>
</form>
"""

class wiz_tabs_setup(wizard.interface):

	def _action_idle(self, cr, uid, data, context):
		return { }

	def _action_inits(self, cr, uid, data, context):
		netsvc.Logger().notifyChannel( 'wiz_tabs_setup() called', netsvc.LOG_DEBUG, " Context="+str(context) )

		VAR_FIELDS.dict = {}


		if 'active_model' not in context:
			VAR_FORM.string = u"""<?xml version="1.0"?>
<form string="Incompatible application">
<separator string="The wizard will close immediately" colspan="4"/>
</form>
"""
			self.states['init']['result']['state'] = [('end','Close')]
			return {}

		VAR_FORM.string = u"""<?xml version="1.0"?>
<form string="%s">
	<separator string="%s" colspan="4"/>
"""	% ( _('Tabs Setup'), _('Check the tabs you want to display, uncheck those which must remains hidden') )

		pool = pooler.get_pool(cr.dbname)
		contracts = pool.get('eagle.contract')

		tabs = []
		if context['active_model'] == 'eagle.config.params':
			eagle_params = pool.get(context['active_model']).browse(cr, uid, context['active_id'])
			if eagle_params.tabs:
				tabs = eagle_params.tabs.split(';')
		if context['active_model'] in ['eagle.contract','res.users']:
			user_id = context['active_model'] == 'res.users' and context['active_id'] or uid
			user = pool.get('res.users').browse(cr, uid, user_id)
			if user.eagle_tabs:
				tabs = user.eagle_tabs.split(';')

		for item in contracts.get_view_selections(cr, uid, context=context):
			k = item[0]
			l = _(item[1])
			
			fld = { 'string': l, 'type': 'boolean' }
			if k in tabs:fld['default'] = '1'

			VAR_FIELDS.dict[k] = fld
			VAR_FORM.string = VAR_FORM.string + """<field name="%s" colspan="4"/>\n""" % k
		
		# Context if this is called from Eagle's Params
		# {'active_id': 1,
		#  'active_ids': [1],
		#  'active_model': u'eagle.config.params',
		#  'department_id': False,
		#  'lang': u'fr_FR',
		#  'project_id': False,
		#  'section_id': False,
		#  'tz': False}
		if context['active_model'] == 'eagle.config.params':
			msg = _('This will be the default setup for all users')
		else:
			msg = _('This will be the setup for the current users')
		VAR_FORM.string = VAR_FORM.string + """<separator string=" " colspan="4"/>
<label string=""" + '\"' + msg + '\"' + """ colspan="4"/>
</form>
"""

		return {}

	def _action_store_tabs_setup(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		tabs = []
		contracts = pool.get('eagle.contract')
		for item in contracts.get_view_selections(cr, uid, context=context):
			k = item[0]
			if data['form'][k]:
				tabs.append(k)

		if context['active_model'] == 'eagle.config.params':
			pool.get(context['active_model']).write(cr, uid, context['active_id'], {'tabs':';'.join(tabs)})
		if context['active_model'] in ['eagle.contract','res.users']:
			user_id = context['active_model'] == 'res.users' and context['active_id'] or uid
			pool.get('res.users').write(cr, uid, user_id, {'eagle_tabs':';'.join(tabs)})
			
		res = { }

		return res

	states = {
		'init': {
			'actions': [_action_inits],
			'result': {'type':'form', 'arch':VAR_FORM, 'fields':VAR_FIELDS, 'state':[('end','Close'),('store','Store')]}
		},
		'store': {
			'actions': [],
			'result': {'type':'action', 'action':_action_store_tabs_setup, 'state':'end'}
		},
		'aborted': {
			'actions': [],
			'result': {'type':'form', 'arch':VAR_FORM, 'fields':VAR_FIELDS, 'state':[('end','Close')]}
		},
	}

wiz_tabs_setup('eagle_wizard_tabs_setup')
