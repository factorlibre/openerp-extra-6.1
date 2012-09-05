# -*- coding: utf-8 -*-
#
#  File: wizard/scheduler_test.py
#  Module: eagle_productivity_crm
#
#  Created by sbe@open-net.ch
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

from osv import osv,fields
import netsvc
import time
from datetime import datetime, timedelta

class scheduler_test(osv.osv):
	_name = 'scheduler.test'
		
	def run_lead_scheduler( self, cr, uid, id, context={}):
		''' Runs leads scheduler.
		'''
		
		lead_obj = self.pool.get('crm.lead')
		lead_obj.run_opportunities_scheduler(cr, uid, id, late_days=5)					
					
		return True

scheduler_test()
