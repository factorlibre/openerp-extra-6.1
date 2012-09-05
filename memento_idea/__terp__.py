# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Enterprise Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://openerp.com>).
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
    'name' : 'Technical Memento example: Idea management module',
    'version' : '1.0',
    'author' : 'OpenERP',
    'description' : '''
Technical Memento example: Idea management module

This module is a part of the OpenERP technical Memento.
This module does not actually implement a complete idea management module,
but rather serves as a technical reference when reading the OpenERP technical memento.
The module source contains most of the examples used in the memento, gathered as 
a single working module.
Do not hesitate to read the (short and simple) source code to understand how all 
the different parts of a module fit together.

This module contains examples for:
 - business objects with all kinds of fields (osv.osv)
 - views of all kinds (form, list, tree, calendar, gantt, chart, ...)
 - one SXW/RML report with a custom parser environment
 - groups and access restriction
 - roles and workflows
 - wizards, actions, and configuration wizards
 - internationalization of labels and terms
 - unit tests
  
    ''',
    'category': 'Human Resources',
    'website': 'http://www.openerp.com',
    'license': 'GPL-3',
    'depends' : [ #list of dependencies, conditioning loadup order
        'base',
    ],
    'update_xml' : [
        'security/groups.xml',           #always load groups first!
        'security/ir.model.access.csv',  #load access rights after groups
        'view/menu.xml',
        'workflow/roles.xml',
        'workflow/workflow.xml',
        'view/views.xml',
        'wizard/cleanup.xml',
        'report/idea.xml',
        'idea_unit_tests.xml',
        ],
    'demo_xml': [
        'demo_data.xml',  #files containing demo_data, for unit_tests for example
    ],
    'active': False,      #do we want automatic installation at new DB creation!
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
