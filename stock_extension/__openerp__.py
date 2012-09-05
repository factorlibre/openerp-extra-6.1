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
    "name" : "Stock Extension",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website": "www.zikzakmedia.com",
    "license" : "GPL-3",
    "category" : "Generic Modules/Others",
    "description": """
    Several improvements for stock module:

    * stock_picking
      - Add 'To Invoice' filter button to the 'Picking In' search view.
      - Remove readonly attribute of the invoice_state field to allow to invoice any stock picking (for example, if someone deletes by mistake the invoice of invoiced picking).
      - Fix bug when the Process Picking Wizard is cancelled: Clears the buffer to prevent that previous lines of picking are added to the current wizard.
      - When the invoice lines are created from an IN picking, the price unit of the picking is added instead of the cost price of the product.
      - Changing the average price of a product: If valuation == 'manual_periodic' is not necessary create an account move for stock variation.
      - Change stock.picking order from newest to oldest.
      - Add the client_order_ref field to the stock.picking model.
      - Makes visible the 'name' field in stock.picking views.
    """,
    "depends" : [
        "sale",
    ],
    "init_xml" : [],
    "update_xml" : [
        'stock_view.xml',
    ],
    "active": False,
    "installable": True
}
