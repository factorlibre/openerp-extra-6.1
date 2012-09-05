# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Gábor Dukai <gdukai@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Product label printing wizards",
    "version" : "1.0",
    "author" : "Gábor Dukai",
    "website" : "http://exploringopenerp.blogspot.com",
    "license" : "GPL-3",
    "category" : "Generic Modules",
    "description": """
    Provides an editable grid to fill in with products and label quantities
    to print. Adds a button on pickings to automatically fill in this grid
    from their data.

    NOTE: The basic functionality works as it is but the button on pickings
    needs the --enable-code-actions parameter for the server.
    Compatibility: tested with OpenERP v5.0
    """,
    "depends" : ["label", "product"],
    "init_xml" : [
    ],
    "demo_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "label_wizard.xml",
        "label_action.xml",
    ],
    "active": False,
    "installable": True
}
