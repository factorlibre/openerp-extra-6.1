# encoding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NaN Projectes de Programari Lliure, S.L. All Rights Reserved
#                       http://www.NaN-tic.com
#    $Id$
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

{
    'name' : "Payment Term Extension",
    'version' : "1.0",
    'author' : "NaN·tic",
    'category': 'Accounting',
    'description': """\
This module extends payment terms with the following features:

- Uses 4 decimal digits instead of 2 for Value Amount field, so percentages can have higher precision.
- Allow using Division, apart from Percentage, so one can ensure only one cent remains in the last term.
- Allow specifing the number of months, which is more usual instead of days in some countries.""",
    'license' : "GPL-3",
    'depends' : [
        'account',
    ],
    'init_xml' : [],
    'update_xml' : [
        'account_view.xml',
    ],
    'test': [
        'test/account_payment_term.yml',
    ],
    'active': False,
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
