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

from math import ceil


def duration_calc(self, cr, uid, ids, field_name, arg, context=None):
    """
    This method allow to calculate time spend for the analytic account of CRM
    """
    res = {}
    for crm in self.browse(cr, uid, ids, context=context):
        res[crm.id] = duration = 0.0
        # check if there is an analytc account in crm
        if hasattr(crm, 'analytic_account_id') and crm.analytic_account_id.id:
            for line in crm.timesheet_ids:
                # add duration only with same analytic account
                if line.analytic_account_id.id == crm.analytic_account_id.id:
                    duration += line.hours
            # If there is a rounding in analytic account so apply at the end
            if crm.analytic_account_id.rounding_duration:
                rounding = crm.analytic_account_id.rounding_duration
                duration = ceil((duration * 100) / (rounding * 100)) * rounding
        else:
            # not analytic account in crm so add all lines
            for line in crm.timesheet_ids:
                duration += line.hours
        res[crm.id] = duration
    return res

def get_crm(self, cr, uid, ids, context=None):
    """
    This method triggers the field function
    """
    result = {}
    for line in self.pool.get('crm.analytic.timesheet').browse(cr, uid, ids, context=context):
        result[line.res_id] = True
    return result.keys()

def get_default_analytic(self, cr, uid, context=None):
    """Gives id of analytic for this case
    @param self: The object pointer
    @param cr: the current row, from the database cursor,
    @param uid: the current user’s ID for security checks,
    @param context: A standard dictionary for contextual values
    """
    if context is None:
        context = {}
    crm_analytic_obj = self.pool.get('crm.analytic.timesheet.configuration')
    crm_analytic_conf_id = crm_analytic_obj.search(cr, uid, [('model', '=', self._name)], offset=0, limit=None, order=None, context=context)
    if not crm_analytic_conf_id:
        return False
    return crm_analytic_obj.browse(cr, uid, crm_analytic_conf_id[0], context=context).analytic_account_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
