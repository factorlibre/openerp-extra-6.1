# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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
    'name': 'Eagle View, base module',
    'version': '4.10.26',
    'category': 'Eagle view/Base',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the base module, it introduces:
	- Basic contract position management
	- Product's recurrencies
	- Waranty managment for each contract position
	- Events configuration: As the Eagle Concept is built around a base module and parallel, optionnal modules, 
      this class let us handle parallel events attach to buttons (for example).
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_config','product'],
    'init_xml': [],
    'update_xml': [
    	"security/eagle_security.xml",
    	"security/ir.model.access.csv",
    	"products_view.xml",
    	"contracts_view.xml",
    	"wizard/wiz_products_2_contracts.xml",
	   	"menu_items.xml",
    	"config_view.xml",
    	"requests_view.xml",
    	"wizard/wiz_tabs_setup.xml",
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}

