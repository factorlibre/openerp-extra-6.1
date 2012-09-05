# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_management
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
    'name': 'Eagle View, management module',
    'version': '4.3.02',
    'category': 'Eagle view/Management',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the management module, it introduces:
	- Sale management: automatic sales and purchases
	- Invoices and analytic entries displayed in the contract view
	- Stock moves, incoming and outgoing products, as well as procurements displayed in the contract view
	
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_project','eagle_base','eagle_config','sale','stock','purchase'],
    'init_xml': [],
    'update_xml': [
    	"sales_view.xml",
    	"contracts_view.xml",
    	"config_view.xml",
    	"invoices_view.xml",
    	"stock_view.xml",
    	"wizard/wiz_mgt_scheduler.xml",
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}
