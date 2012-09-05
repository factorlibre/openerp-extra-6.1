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
    "name" : "Stock Supplier Average Price",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website": "www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category" : "Generic Modules/Inventory Control",
    "description": """
    This module adds cost price in the Process Wizard of the Supplier Return \
Picking, and remove it in the Process Wizard of the Customer Return Picking.

Changes the default formula used in OpenERP to compute the new \
average price of a product in stock in returned pickings, by the next one:

                                      (current_cost_price x current_stock) - \
(returned_cost_price x returned_stock)
new_average_price = -----------------------------------------------------------\
--------------------------------------------- 
                                                           current_stock - \
returned_stock
    """,
    "depends" : [
        "stock",
    ],
    "init_xml" : [],
    "update_xml" : [
    ],
    "active": False,
    "installable": True
}
