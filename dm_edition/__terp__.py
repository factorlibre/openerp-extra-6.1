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
    "name" : "Edition for DM",
    "version" : "0.1",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Direct Marketing",
    "description": """
            This module adds paper edition management for Direct Marketing.
            It allows the grouping of documents based on selection criteria and the selection of printers and printers trays for printing of paper documents.
            """,
    "depends" : ["dm"],
    "init_xml" : [],
    "demo_xml" : [
                'dm_edition_demo.xml',            
    ],

    "update_xml" :[
            "security/ir.model.access.csv",
            'dm_edition_view.xml',
            'dm_edition_wizard.xml',
            'dm_edition_data.xml',
            ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
