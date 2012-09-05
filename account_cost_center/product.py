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

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'property_account_cost_center' : fields.property(
											'account.account',
											type = 'many2one',
											relation='account.account',
											string="Cost Center Account",
											method=True,
											view_load=True,
											help="This account will be used to value cost center for the current product"),
        'property_account_charges' : fields.property(
											'account.account',
											type = 'many2one',
											relation='account.account',
											string="Charges Account",
											method=True,
											view_load=True,
											help="This account will be used to value charges for the current product"),
    }

product_template()
