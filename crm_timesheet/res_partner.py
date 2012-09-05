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

class res_partner_crm_analytic(osv.osv):
    """
    Define one analytic account by section,
    to disable the analytic account for a section, add line with section and
    not fill the analytic account
    """
    _name = 'res.partner.crm.analytic'
    _description = 'CRM Partner Analytic Account'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'crm_model_id': fields.many2one('crm.analytic.timesheet.configuration', 'Model', required=True, help="Model of crm"),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account',\
                                               ondelete='cascade',\
                                               help="Ananlytic account by default for this model of crm and for this partner",\
                                               domain="[('partner_id', '=', partner_id), ('state', '=', 'open'), ('type', '=', 'normal')]"),
    }

res_partner_crm_analytic()

class res_partner(osv.osv):
    """
    Add a new tab on partner, to select the analytic account by section
    """
    _inherit = 'res.partner'

    _columns = {
        'crm_analytic_ids': fields.one2many('res.partner.crm.analytic', 'partner_id', 'CRM Analytic Account'),
    }

res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
