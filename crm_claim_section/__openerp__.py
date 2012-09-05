# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
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
    "name" : "Customer & Supplier Relationship Management Section",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules/CRM & SRM",
    "description": """
    Add section when recive message_new (fetchmail)
    Email Section is Sales Team (crm.case.section)
    Everyone section, you need add email in Sales/Configuration/Sales/Sales Team -> Repply to
    """,
    "license" : "AGPL-3",
    "depends" : [
        "crm_claim",
    ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'crm_claim_view.xml',
    ],
    "active": False,
    "installable": True
}
