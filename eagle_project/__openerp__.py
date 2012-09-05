# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_project
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
    'name': 'Eagle View, projects module',
    'version': '4.2.23',
    'category': 'Eagle view/Projects',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the projects module, it links the contract to the projects:
	- 1 main project
	- 2 sub-projects: 1 for installation + 1 for production (recurrent items)
	- the main project, the linked tasks, works and analytic items are visible in their respective tabs
	
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_config','eagle_base','project_mrp',"hr_timesheet_invoice", "project_timesheet"],
    'init_xml': [],
    'update_xml': [
    	"projects_view.xml",
    	"contracts_view.xml",
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}
