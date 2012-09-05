# -*- coding: utf-8 -*-
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


{
    'name': 'Backport of the accounting reports of v6',
    'version': '1.1',
    'category': 'Generic Modules/Accounting',
    'description': """This module contains the financial and accounting reports defined in the v6 with few changements in order to get them compatible for v5. The following reports are included:
    * Account Balance
    * General Ledger
    * Partner Ledger
    * Partner Balance
    * Partner Aged Balance
    * Print journal
    * Central Journal
    * General Journal
    """,
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        'wizard/account_report_account_balance_view.xml', 
        'wizard/account_report_partner_balance_view.xml',
        'wizard/account_report_aged_partner_balance_view.xml',
        'wizard/account_report_general_journal_view.xml',
        'wizard/account_report_partner_ledger_view.xml',
        'wizard/account_report_central_journal_view.xml',    
        'wizard/account_report_general_ledger_view.xml',
        'wizard/account_report_print_journal_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
