# -*- encoding: utf-8 -*-
#########################################################################
#
#    Kettle connector for OpenERP
#    Copyright (C) 2010 Sébastien Beau <sebastien.beau@akretion.com>
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
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
#########################################################################

{
    "name" : "Kettle connector",
    "version" : "1.0",
    "category": "Generic Modules/Other",
    "license": "AGPL-3",
    "depends" : ['base_scheduler_creator'],
    "author" : "Akretion",
    "description": """Kettle connector
""",
    "website" : "http://www.akretion.com/",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
            "kettle.xml",
            'security/kettle_security.xml',
            'security/ir.model.access.csv',
                    ],
    "active": False,
    "installable": True,
}
