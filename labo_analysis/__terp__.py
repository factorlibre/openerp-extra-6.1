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
    "name" : "Labo analysis create Progenus project",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Industries",
    "depends" : ["base", "account", "product", "stock","crm","labo_stock","labo_tool"],
    "init_xml" : ["labo_analysis_data.xml",'labo_analysis_view.xml',"labo_analysis_sequence.xml",'labo_analysis_report.xml','labo_analysis_wizard.xml','analysis_view.xml','analysis_view_empche.xml', 'labo_analysis_view2.xml'],
    "demo_xml" : [],#'labo_anlysis_demo.xml'],
    "description": "Progenus project Labo analysis object",
    "update_xml" : ["labo_analysis_data.xml",'labo_analysis_view.xml',"labo_analysis_sequence.xml",'labo_analysis_report.xml','labo_analysis_wizard.xml','analysis_view.xml','analysis_view_empche.xml','labo_analysis_view2.xml'],
    "active": False,
    "installable": True
}
