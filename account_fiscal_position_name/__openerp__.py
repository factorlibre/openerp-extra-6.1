# -*- coding: utf-8 -*-
##############################################################################
#
#    account_fiscal_position_name module for OpenERP, Show name instead of description
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>) 
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of account_fiscal_position_name
#
#    account_fiscal_position_name is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_fiscal_position_name is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Fiscal Position Name',
    'version': '1.0',
    'category': 'Account',
    'description': """Show name instead of description""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'account',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        #'security/groups.xml',
        #'security/ir.model.access.csv',
        #'view/menu.xml',
        #'wizard/wizard.xml',
        #'report/report.xml',
    ],
    'demo_xml': [],
    'test': [],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
