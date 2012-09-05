# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2010 Pexego Sistemas Informáticos. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
Extensions to the cash statements to add analytical accounting features.
"""

__authors__ = [
    "Borja López Soilán (Pexego) <borjals@pexego.es>"
]

from osv import osv, fields


class cash_statement_line_type(osv.osv):
    """
    Extend the Cash Statement Line Type to add the analytic account.
    """
    _inherit = 'account.bank.statement.line.type'

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
    }

cash_statement_line_type()



class cash_statement_line(osv.osv):
    """
    Extend the cash statement lines to add the analytic-related behaviour.
    """
    _inherit = 'account.bank.statement.line'


    def cash_line_on_change_line_type_id(self, cr, uid, line_id, partner_id, original_type, line_type_id, context=None):
        """
        Update the analytic account when the line type changes.
        """
        res = super(cash_statement_line, self).cash_line_on_change_line_type_id(cr, uid, line_id, partner_id, original_type, line_type_id, context=context)

        if line_type_id:
            line_type = self.pool.get('account.bank.statement.line.type').browse(cr, uid, line_type_id)

            #
            # Set the analytic account
            #
            if line_type.analytic_account_id:
                res['value']['analytic_account_id'] = line_type.analytic_account_id.id
        
        return res
cash_statement_line()

