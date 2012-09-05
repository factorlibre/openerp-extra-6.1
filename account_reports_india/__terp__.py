# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Accounting Reports - Indian Accounting",
    "version" : "1.0",
    "depends" : [
        "account_voucher",
    ],
    "author" : "Tiny & Axelor",
    "description": """Accounting Reports - Indian Accounting
Modules gives the 3 most Important Reports for the Indian Accounting
* Trial Balance
* Profit and Loss Account
* Balance Sheet
    """,
    "website" : "http://tinyerp.com/module_account.html",
    "category" : "Generic Modules/Indian Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
                   
    ],
    "update_xml" : [ "account_report.xml" 
    ],
    "active": False,
    "installable": True
}
