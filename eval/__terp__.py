# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
    'name': 'Evaluations of Employees',
    'version': '1.0',
    'category': 'Generic Modules/Evaluation for employees',
    'description': """
                      Evaluation of employee can be done by its manager and by its sub-ordinates.""",
    'author': 'Tiny',
    'depends': ['base','product','hr', 'hr_contract'],
    'init_xml': [],
    'update_xml': ['eval_view.xml',
                   'eval_report.xml',
                   'eval_data.xml',
                   'eval_wizard.xml',
                   'security/eval_security.xml',
                   'security/ir.model.access.csv'
    ],
    'demo_xml': ['eval_demo.xml'],
    'installable': True,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
