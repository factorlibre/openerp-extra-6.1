# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_inv_scheduler.py
#  Module: eagle_management
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

from osv import osv, fields
import time

class wizard_setup_management_scheduler(osv.osv_memory):
	_name = 'eagle.setup_mgt_sched'
	_description = 'Setup an Eagle Management Scheduler'

	def setup_scheduler(self, cr, uid, ids, context=None):
		if not context:
			context = {}
		
		crons = self.pool.get( 'ir.cron' )
		cron_ids = crons.search( cr, uid, [('model','=','eagle.contract'),('function','=','run_mgt_scheduler')], context=context )
		if not cron_ids or len(cron_ids) < 1:
			vals = {
				'model': 'eagle.contract',
				'function': 'run_mgt_scheduler',
				'name': 'Eagle Management Scheduler',
				'interval_number': 1,
				'interval_type': 'days',
				'numbercall':-1,
				'nextcall': time.strftime('%Y-%m-%d 23:00:00'),
				'args': '()',
				'user_id': 1,
			}
			res = crons.create( cr, uid, vals, context=context )

		res = {
			'domain': str([]),
			'name': 'Crons',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'ir.cron',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'context': {'active_test': False},
		}
		return res

wizard_setup_management_scheduler()
