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
    "name" : "Account Analytic Package - To configure Analytic Account for product packages",
    "description": """The Module allows to configure analytic account for product packages.
    Views for total and monthly product packages weight, Amount analysis.""",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Accounting",
    "module": "",
    "website": "http://www.openerp.com",
    "depends" : ["account","product","crm"],
    "init_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "account_analytic_package_view.xml"
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

