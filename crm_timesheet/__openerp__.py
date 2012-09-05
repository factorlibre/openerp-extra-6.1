# -*- coding: utf-8 -*-
##############################################################################
#
#    crm_timesheet module for openerp, crm timesheet
#    copyright (c) 2011 syleam info services (<http://www.syleam.fr/>) 
#              sebastien lange <sebastien.lange@syleam.fr>
#
#    this file is a part of crm_timesheet
#
#    crm_timesheet is free software: you can redistribute it and/or modify
#    it under the terms of the gnu general public license as published by
#    the free software foundation, either version 3 of the license, or
#    (at your option) any later version.
#
#    crm_timesheet is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'CRM Timesheet',
    'version': '0.1',
    'category': 'Generic Modules/Human Resources',
    'description': """
        This module lets you transfer the entries under CRM Management to
        the Timesheet line entries for particular date and particular user with the effect of creating, editing and deleting either ways.
    """,
    'author': 'SYLEAM Info Services',
    'website': 'http://www.Syleam.fr/',
    'depends': [
        'crm',
        'hr_timesheet',
    ],
    'init_xml': [],
    'update_xml': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'analytic_view.xml',
        'company_view.xml',
        'crm_lead_view.xml',
        'crm_opportunity_view.xml',
        'crm_phonecall_view.xml',
        'res_partner_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
