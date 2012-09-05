# -*- coding: utf-8 -*-
##############################################################################
#
#    crm_timesheet module for openerp, CRM timesheet
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'crm_time_mode_id': fields.many2one('product.uom', 'CRM Time Unit',
            help='This will set the unit of measure used in CRM.\n' \
"If you use the timesheet linked to CRM (crm_timesheet module), don't " \
"forget to setup the right unit of measure in your employees.",
        ),
    }
res_company()

