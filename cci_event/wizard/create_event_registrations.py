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
<form string="Create registrations for this event">
    <field name="event_id" coslpan="4"/>
</form>
"""
fields = {
      'event_id': {'string':'Event', 'type':'many2one', 'readonly':False, 'relation': 'event.event', 'required':True},
          }

def _create_reg_event(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    event_obj = pool_obj.get('event.event')
    registration_obj = pool_obj.get('event.registration')
    reg_datas = registration_obj.browse(cr, uid, data['ids'])
    for reg in reg_datas:
        registration_obj.copy(cr, uid, reg.id,{'event_id':data['form']['event_id']})
    return {}

def _open_reg(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    reg_ids = []
    cr.execute('select id from event_registration where event_id = %s'%(data['form']['event_id']))
    map(lambda x:reg_ids.append(x[0]), cr.fetchall())
    model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','event_registration_form')])
    resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
    return {
            'domain': "[('id','in', ["+','.join(map(str, reg_ids))+"])]",
            'name': 'Registrations',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'event.registration',
            'views': [(False,'tree'), (resource_id,'form')],
            'type': 'ir.actions.act_window'
        }

class confirm_registration(wizard.interface):
    states = {
        'init': {
           'actions': [],
           'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end', 'Cancel'), ('create', 'Create')]}
            },
        'create': {
            'actions' : [_create_reg_event],
           # 'result' : {'type':'state', 'state':'end'}
            'result' : {'type':'action', 'action':_open_reg, 'state':'end'}
            },
    }
confirm_registration("event.create_registrations")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
