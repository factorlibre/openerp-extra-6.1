# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: ons_advanced_multi_company
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
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
    'name': 'Open-Net Productivity Add-ons: product',
    'version': '1.2.12',
    'category': 'Generic Modules/Open-Net',
    'description': """
        This module increases your productivity with complementary tools:
            * a product may have a type that depends on the company from where it is seen
            * a product may also have supply and procurement methods that depend on the company from where they are seen ( >= V1.2 )
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['product'],
    'init_xml': [],
    'update_xml': [ "wizard/wiz_setup_product_type.xml" ],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}
