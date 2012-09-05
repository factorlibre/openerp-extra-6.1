# -*- coding: utf-8 -*-
##############################################################################
#
#    crm_timesheet module for OpenERP, CRM Timesheet
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>) 
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of crm_timesheet
#
#    crm_timesheet is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    crm_timesheet is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'

    _columns = {
        'rounding_duration': fields.float('Rouding Duration', help="This field allow to rounding duration of cases.\nExample :\n- value to 00:15, we have a case with timesheet to 00:35, the duration will be 00:45\n- value to 00:15, we have a case with timesheet to 00:30, the duration will be 00:30"),
    }

account_analytic_account()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
