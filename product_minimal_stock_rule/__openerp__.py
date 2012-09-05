# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-2011 ToolPart Team LLC (<http://toolpart.hu>).
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
    "name" : "Automatic Minimal Stock Rules",
    "version" : "1.0",
    "depends" : [
    "stock", "product", "procurement"
    ],
    "author" : "ToolPart Team LLC.",
    "description": """
        Adds a minimal stock rule to newly created products.
    """,
    "website" : "http://toolpart.hu/",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "product_minimal_stock_rule_view.xml",
    ],
    'test': ['test/test_rule.yml',],
    "active": False,
    "installable": True,
    "web": False,
}
