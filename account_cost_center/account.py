# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields

class account_account(osv.osv):
    _name = 'account.account'
    _inherit = 'account.account'
    _columns = {
        'property_account_debit' : fields.property(
											'account.account',
											type = 'many2one',
											relation='account.account',
											string="Debit Account",
											method=True,
											view_load=True,
											help="This account will be used to make another journal entry as debit account"),
        'property_account_credit' : fields.property(
											'account.account',
											type = 'many2one',
											relation='account.account',
											string="Credit Account",
											method=True,
											view_load=True,
											help="This account will be used to make another journal entry as creditt account"),
    }

account_account()
