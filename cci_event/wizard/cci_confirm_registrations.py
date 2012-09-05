# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import wizard
import netsvc
import pooler
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Confirm Registration">
    <field name="message" width="400"/>
</form>
"""
fields = {
      'message': {'string':'Result', 'type':'char', 'readonly':True, 'size':64},
          }

def _confirm_reg(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    registration_obj = pool_obj.get('event.registration')
    reg_datas = registration_obj.browse(cr, uid, data['ids'])
    ids_case = []
    for reg in reg_datas:
        if not reg.check_ids:
            ids_case.append(reg.case_id)
    reg_ids = registration_obj.search(cr, uid, [('state', '=', 'draft'), ('id', 'in', ids_case)])
    if not reg_ids:
        return {'message' : 'No Draft Registration Available'}
    registration_obj.write(cr, uid, reg_ids, {'state':'open',})
    registration_obj._history(cr, uid, reg_ids, 'Open', history=True)
    registration_obj.mail_user(cr, uid, reg_ids)
    return {'message' : 'All Draft Registration confirmed'}

class confirm_registration(wizard.interface):
    states = {
        'init' : {
           'actions' : [_confirm_reg],
           'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end', 'Ok')]}
            },
    }
confirm_registration("event.confirm_registrations")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: