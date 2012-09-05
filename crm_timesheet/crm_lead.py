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
import crm_operators


class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _name = "crm.lead"

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete='cascade', ),
        'timesheet_ids': fields.one2many('crm.analytic.timesheet', 'res_id', 'Messages', domain=[('model', '=', _name)]),
        'duration_timesheet': fields.function(crm_operators.duration_calc, method=True, string='Hours spend',
            store = {
                'crm.lead': (lambda self, cr, uid, ids, c={}: ids, ['timesheet_ids'], 10),
                'crm.analytic.timesheet': (crm_operators.get_crm, ['hours', 'analytic_account_id'], 10),
            },)
    }

    _defaults = {
         'analytic_account_id': crm_operators.get_default_analytic,
    }

    def onchange_partner_id(self, cr, uid, ids, part, email=False):
        """This function returns value of partner address based on partner
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of case IDs
        @param part: Partner's id
        @email: Partner's email ID
        """
        if not part:
            return {'value': {'partner_address_id': False,
                            'email_from': False, 
                            'phone': False,
                            'analytic_account_id': False,
                            }}
        partner_obj = self.pool.get('res.partner')
        addr = partner_obj.address_get(cr, uid, [part], ['contact'])
        partners = partner_obj.browse(cr, uid, part)
        data = {'partner_address_id': addr['contact']}
        data.update(self.onchange_partner_address_id(cr, uid, ids, addr['contact'])['value'])
        for timesheet in partners.crm_analytic_ids:
            if timesheet.crm_model_id.model == self._name:
                data['analytic_account_id'] = timesheet.analytic_account_id.id
        return {'value': data}

    def create(self, cr, uid, values, context=None):
        """
        Add model in context for crm_analytic_timesheet object
        """
        if context is None:
            context = {}
        # Add model for crm_timesheet
        context['model'] = self._name
        return super(crm_lead, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        """
        Add model in context for crm_analytic_timesheet object
        """
        if context is None:
            context = {}
        # Add model for crm_timesheet
        context['model'] = self._name
        return super(crm_lead, self).write(cr, uid, ids, values, context=context)

crm_lead()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
