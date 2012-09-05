# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name" : "Internet Domain",
    "author" : "Zikzakmedia SL",
    "website" : "http://www.zikzakmedia.com",
    "license" : "AGPL-3",
    "description" : """
Organize your domains and services
Tools -> Domain
* Domains
* Renewals
* Products/Services
* Network
* Send email expiration domain with Schuddle Action and Power Email
* Invoice renewal domain
    """,
    "version" : "0.1",
    "depends" : [
        "base",
        "product",
        "account",
        "network",
        "poweremail"
    ],
    "init_xml" : [],
    "update_xml" : [
        "security/internetdomain_security.xml",
        "security/ir.model.access.csv",
        "internetdomain_view.xml",
        "internetdomain_report.xml",
        "wizard/make_invoice_view.xml",
        "internetdomain_data.xml",
        "company_view.xml",
    ],
    "category" : "Product",
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

