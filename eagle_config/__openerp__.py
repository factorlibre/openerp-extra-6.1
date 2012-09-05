# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_config
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
    'name': 'Eagle View, config module',
    'version': '4.3.02',
    'category': 'Eagle view/Config',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the base module, it introduces:
	- Events configuration: As the Eagle Concept is built around a base module and parallel, optionnal modules, 
    this class let us handle parallel events attach to buttons (for example).
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['product'],
    'init_xml': [ 'setup.xml' ],
    'update_xml': [
    	"security/eagle_security.xml",
    	"security/ir.model.access.csv",
    	"config_view.xml",
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}

