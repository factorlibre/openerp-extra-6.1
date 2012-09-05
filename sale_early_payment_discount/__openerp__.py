# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Early payment discount",
    "description" : """Pexego - Allow set an early payment discount in sale orders, invoices and picking lists. Includes:
                        -A new sales report overriding default Order Report.
                        -A new product category: System Products (a new account for E.P. will be set here)
                        -A new product for early payment discounts (an output stock account for discounts can be set here)
                    """,
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base", "product", "account", "sale", "decimal_precision"],
    "category" : "Payment",
    "init_xml" : [],
    "update_xml" : ['security/ir.model.access.csv',
                    'data/product_product.xml',
                    'partner_payment_term_early_discount_view.xml',
                    'partner_view.xml',
                    'payment_term_view.xml',
                    'sale_view.xml',
                    'account_invoice_view.xml',
                    'sale_report.xml',
                    'product_category_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
