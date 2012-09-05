# -*- coding: utf-8 -*-
##############################################################################
#
#    civilengineering module for OpenERP
#    Copyright (C) 2008-2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#       Raimon Esteve <resteve@zikzakmedia.com> All Rights Reserved.
#       Jesús Martín <jmartin@zikzakmedia.com>
#
#    This file is a part of civil_engineering
#
#    civilengineering is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    civilengineering is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Civil Engineering",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category" : "Generic Modules/Projects & Services",
    "description" : """Civil Engineering Works:

* Adds a new menu to manage civil engineering works: Location, agents and other consultancies, work data, structure data and assignments to projects.

* New entities for civil engineering works (all these entities have an hierarchical structure and a tree view, civil engineering works can be filtered from the tree view):
    * Work Class
    * Work Use
    * Structure Type
    * Foundation Type
    * Structural Model Abstraction
    * Structural Modeling Software. 

* Adds a new tab in the project form, sale form and purchase form to relate these objects to civil engineering works
""",
    "version" : "0.1",
    "depends" : ["base","project",'sale','purchase'],
    "init_xml" : [],
    "update_xml" : [
        'security/civil_engineering_security.xml',
        'security/ir.model.access.csv',
        "civil_engineering_view.xml",
        "sale_view.xml",
        "purchase_view.xml",
        "project_view.xml",
    ],
    "active": False,
    "installable": True
}
