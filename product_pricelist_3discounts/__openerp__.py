# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
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
    "name" : "Product Pricelist 3 Discounts",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website": "www.zikzakmedia.com",
    "license" : "GPL-3",
    "category": "Generic Modules",
    "description": """This module:
* Adds three discounts to each pricelist item and computes the discount name from them.
* Adds the discount name in the sale order lines and invoice lines when product changes.
* If an invoice is computed from a sale order or from a picking, the discount names in invoice lines are obtained from the sale order lines 
    """,
    "depends" : [
        "product_pricelist_allinone",
        "sale",
    ],
    "init_xml" : [],
    "update_xml" : [
        'invoice_view.xml',
        'pricelist_view.xml',
        'sale_view.xml',
    ],
    "active": False,
    "installable": True
}
