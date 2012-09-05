# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Serpent Consulting Services (<http://www.serpentcs.com>).
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
    'name': 'Mrp operation extension',
    'version': '1.0',
    'website': 'http://www.serpentcs.com',
    'category': 'Generic Modules/Production',
    'description': """
        This module will modify workorder workflow so that when we start production order
        it will start only first workorder instead of starting all workorders.
    """,
    'author': 'Serpent Consulting Services',
    'depends': ['mrp_operations'],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'test':[],
    'active': False,
    'certificate': '',
}
