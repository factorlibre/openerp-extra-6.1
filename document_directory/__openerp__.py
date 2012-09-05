# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
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
    "name" : "Document Management System - Default Directory",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules/Others",
    "description": """
    Document Directory default value is Document directory.
    This module change default value parent_id and get directory from object.
    Examples:
    * Attach file in product, default directory is "Products". 
    * Attach file in partner, default directory is "Partners". 
    If don't exists directory object, use "Document" directory.
    You need in directories, select Parent Model without Parent Directory.
    """,
    "license" : "AGPL-3",
    "depends" : [
        "document",
    ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
    ],
    "active": False,
    "installable": True
}
