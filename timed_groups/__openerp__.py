# -*- coding: utf-8 -*-
##############################################################################
#
#    school module for OpenERP
#    Copyright (C) 2010 Tecnoba S.L. (http://www.tecnoba.com)
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
#    Copyright (C) 2011 Zikzakmedia S.L. (http://www.zikzakmedia.com)
#       Jesús Martín Jiménez <jmargin@zikzakmedia.com> All Rights Reserved.
#
#    This file is a part of school module
#
#    school OpenERP module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    school OpenERP module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Groups Management',
    'version' : '0.0.1',
    'author' : 'Pere Ramon Erro Mas (Tecnoba)',
    'website' : 'http://www.tecnoba.com',
    'description' : """
Base module for extends. It serves to manage the participations time in a groups.
""",
    "category" : "Generic Modules/Others",
    "depends": [
        'base_contact',
    ],
    'demo_xml' : [],
    'update_xml' : [
        'security/ir.model.access.csv',
        'timed_groups.xml',
        'wizards/wizard_create_group_assignations.xml',
    ],
    'active' : False,
    'installable' : True,
}

