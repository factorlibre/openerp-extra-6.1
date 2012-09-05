# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_crm
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
    'name': 'Eagle View, CRM module',
    'version': '4.11.34',
    'category': 'Eagle view/CRM',
    'description': """This module increases your productivity by introducing a complete contracts management.
This is the CRM module, it introduces:
	- new wizards:
		- contact for opportunity
		- new lead
		- new opportunity
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_base','project_issue','base_contact','crm_claim'],
    'init_xml': [],
    'update_xml': [
    	'wizard/new_contact_for_opport_view.xml',
    	'wizard/new_lead_view.xml',
    	'wizard/new_opportunity_view.xml',
    	'wizard/new_contact_for_partner_view.xml',
		'wizard/crm_partner_to_opp_view.xml',
    	"leads_view.xml",
		"meetings_view.xml",
		"partner_contacts_view.xml",
		"partners_view.xml",
		"phonecalls_view.xml",
    	"contracts_view.xml",
    	"opportunities_view.xml",
		'claims_view.xml',
		'wizard/wiz_crm_scheduler.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}
