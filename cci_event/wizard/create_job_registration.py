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
import pooler

form = """<?xml version="1.0"?>
<form string="Create Registration">
    <field name="event_id" width="400"/>
</form>
"""
fields = {
      'event_id': {'string':'Event', 'type':'many2one', 'readonly':False, 'relation': 'event.event', 'required':True},
      }

form_result = """<?xml version="1.0"?>
<form string="Result">
    <label colspan="2" string="Registration created" align="0.0"/>
</form>
"""
fields_result = {}

def _create_reg(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    obj_reg = pool.get('event.registration')
    obj_job = pool.get('res.partner.job')
    obj_event = pool.get('event.event')
    event = data['form']['event_id']
    event = obj_event.browse(cr, uid, [event], context=context)[0]
    reg_ids = []
    contact_ids = []
    filter_contacts = []
    for job in obj_job.browse(cr, uid, data['ids'], context=context):
        contact_ids.append(job.contact_id.id)

    cr.execute('select e.id, e.contact_id from event_registration as e  \
                left join res_partner_contact as c on c.id=e.contact_id \
                where e.event_id = %s and c.id in ('+','.join(map(str, contact_ids))+') \
                group by e.contact_id,e.id', (event.id,))
    regs = cr.dictfetchall()
    if regs:
        map(lambda x: filter_contacts.append(x['contact_id']), regs)
    contacts_list = []
    for job in obj_job.browse(cr, uid, data['ids'], context=context):
        if job.contact_id.id in filter_contacts or job.contact_id.id in contacts_list:
            continue
        data = obj_reg.onchange_partner_id(cr, uid, [], job.name.id, event.id)
        data2 = obj_reg.onchange_contact_id(cr, uid, [], job.contact_id.id, job.name.id)
        data['value'].update(data2['value'])
        data = data['value']

        data.update({'event_id': event.id,
                'partner_id': job.name.id,
                'contact_id': job.contact_id.id,
                'invoice_label': event.product_id.name,
                'name': 'Registration'
                })
        reg_id = obj_reg.create(cr, uid, data, context=context)
        contacts_list.append(job.contact_id.id)
        reg_ids.append(reg_id)
    return {'reg_ids': reg_ids}

class job_registration(wizard.interface):
    def _open_reg(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        case_ids = []
        if data['form']['reg_ids']:
            cr.execute('select case_id from event_registration where id in ('+','.join(map(str, data['form']['reg_ids']))+')')
            map(lambda x:case_ids.append(x[0]), cr.fetchall())
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','event_registration_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
        return {
            'domain': "[('id','in', ["+','.join(map(str, case_ids))+"])]",
            'name': 'Registrations',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'event.registration',
            'views': [(False,'tree'), (resource_id,'form')],
            'type': 'ir.actions.act_window'
        }

    states = {
        'init': {
           'actions': [],
           'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end', 'Cancel'), ('create', 'Create')]}
            },
        'create': {
            'actions': [_create_reg],
            'result': {'type': 'form', 'arch':form_result, 'fields': fields_result, 'state':[('open', 'Open Registrations'), ('end', 'Ok')]}
            },
        'open' : {
            'actions' : [],
            'result' : {'type':'action', 'action':_open_reg, 'state':'end'}
        },
    }
job_registration("event.job_registration")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
