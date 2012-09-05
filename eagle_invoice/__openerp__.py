# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_invoice
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
    'name': 'Eagle View, invoices module',
    'version': '4.3.24',
    'category': 'Eagle view/Invoices',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the financial module, it introduces:
	- your invoice lines appear in the contract's view, in two tabs:
		- current invoice lines, in draft state
		- past invoice lines, in opened/closed state
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_project'],
    'init_xml': [],
    'update_xml': [
    	"invoices_view.xml",
    	"contracts_view.xml",
    	"config_view.xml",
    	"wizard/wiz_inv_scheduler.xml",
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}

