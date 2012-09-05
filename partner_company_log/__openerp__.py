# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Partner Company Log",
    "version": "0.1",
    "author": "Zikzakmedia SL",
    "website": "http://www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category": "Generic Modules/Base",
    "description": """Allows to track every user/company operation on all the objects of the system, saving this info in a partner computed from the object.

    The administrator can define rules for read, write and delete on objects.
    
    The log history could be checked in the partner form.""",
    "depends": [
        'base',
    ],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
        'security/ir.model.access.csv',
        'partner_company_log_view.xml',
        'partner_view.xml',
    ],
    "installable": True,
}
