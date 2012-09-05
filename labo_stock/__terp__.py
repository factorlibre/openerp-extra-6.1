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

{
	"name" : "Labo stock create Progenus project",
	"version" : "1.0",
	"author" : "Tiny",
	"category" : "Enterprise Specific Modules/Food Industries",
	"depends" : ["base", "account", "product", "stock","sale"],
	"update_xml" : ["labo_stock_view.xml", "labo_stock_wizard.xml","labo_stock_report.xml"],
	"demo_xml" : [],
	"description": "Progenus project Labo stock object",
	"active": False,
	"installable": True
}
