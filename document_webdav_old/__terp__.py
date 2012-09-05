# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
#
# Use the custom module to put your specific code in a separate module.
#
{
	"name" : "Integrated Document Management System",
	"version" : "1.0",
	"author" : "Tiny",
	"category" : "Generic Modules/Others",
	"website": "http://www.openerp.com",
	"description": """This is a complete document management system:
	* WebDav Interface
	* User Authentification
	* Document Indexation
""",
	"depends" : ["base"],
	"init_xml" : ["document_data.xml"],
	"update_xml" : ["document_view.xml"],
	"demo_xml" : ["document_demo.xml"],
	"active": False,
	"installable": True
}
