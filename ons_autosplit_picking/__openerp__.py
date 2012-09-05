# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: ons_autosplit_picking
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Open-Net tools: picking autosplit tool',
    'version': '1.1.08',
    'category': 'Generic Modules/Open-Net',
    'description': """
        This module lets you split a picking with one move into n move
        an external CSV file is used to setup the fields such as a tracking number and a production lot
        each new stock move will be setup for a quantity=1, that means that your CSV file must contains
        the same number of lines as the original stock move has as quantity.
""",
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['stock'],
    'init_xml': [
		'security/ir.model.access.csv',
		],
    'update_xml': [
		'wizard/import_n_split_view.xml',
		'stock_view.xml',
	],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
