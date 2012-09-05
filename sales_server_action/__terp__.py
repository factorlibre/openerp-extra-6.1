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
        "name" : "Sales Server Action",
        "version" : "5.0",
        "author" : "Tiny",
        "website" : "http://www.openerp.com",
        "category" : "Vertical Modules/Parametrization",
        "description": """Server Action for Sales Management
You will get 2 actions, for the demonstration for the Server Action
that will helps you to customize the Business process
* One Invoice / Each Sales Order Line
* Two Invoice for One Sales Order
** Invoice for the Stokable products
** Invoice for the Service product
""",
        "depends" : ["sale"],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : [
            "sale_server_action_data.xml",
            "sale_server_action_condition.xml"
        ],
        "installable": True
} 
