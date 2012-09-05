# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import time

import wizard
import pooler

form = """<?xml version="1.0"?>
<form string="Summary of Created Legalization">
    <field name="leg_created"/>
    <newline />
    <field name="leg_rejected"/>
    <newline />
    <field name="leg_rej_reason" width="400"/>
</form>
"""
fields = {
    'leg_created': {'string':'Legalization Created', 'type':'char', 'readonly':True},
    'leg_rejected': {'string':'Legalization Rejected', 'type':'char', 'readonly':True},
    'leg_rej_reason': {'string':'Error Messages', 'type':'text', 'readonly':True},
         }

introform = """<?xml version="1.0"?>
<form string="Summary of Created Legalization">
    <field name="leg_type_id"/>
</form>
"""
introfields = {
    'leg_type_id': {'type':'many2one','relation':'cci_missions.dossier_type','string':'Dossier Type','required':True,'domain':"[('section','=','legalization')]"},
         }


def _create_legalization(self, cr, uid, data, context):
    obj_pool = pooler.get_pool(cr.dbname)
    obj_certi = obj_pool.get('cci_missions.certificate')
    data_certi = obj_certi.browse(cr, uid, data['ids'])
    list_leglization = []
    leg_create = 0
    leg_reject = 0
    leg_rej_reason = ""
    type_id = data['form']['leg_type_id']
    type_rec = obj_pool.get('cci_missions.dossier_type').browse(cr, uid, type_id)

    for data in data_certi:
        leg_create = leg_create + 1
        prod_lines = []

        map(lambda x: prod_lines.append(x.id), data.product_ids)
        if data.order_partner_id.membership_state in ('none','canceled'): #the boolean "Apply the member price" should be set to TRUE or FALSE when the partner is changed in regard of the membership state of him.
            is_member = False
        else:
            is_member = True

        leg_id =obj_pool.get('cci_missions.legalization').create(cr, uid, {
            'type_id': type_id,
            'date': data.date,
            'order_partner_id': data.order_partner_id.id,
            'quantity_original': data.quantity_original,
            #'text_on_invoice': data.text_on_invoice,
            'asker_name': data.asker_name,
            'sender_name': data.sender_name,
            'state': data.state,
            'goods': data.goods,
            'goods_value': data.goods_value,
#            'destination_id': data.destination_id.id, => valid4certificate
            'quantity_copies': 0,
            'quantity_original': 0,
            'to_bill': data.to_bill,
            'member_price': is_member,
            'destination_id': data.destination_id and data.destination_id.id or False,
#            'product_ids': [(6, 0, prod_lines)] => no need
            })
        cr.execute('select dossier_id from cci_missions_legalization where id='"'%s'"''%(leg_id))
        doss=cr.fetchone()
        leg_ids = []
        map(lambda x: leg_ids.append(x.id), data.legalization_ids)
        leg_ids.append(leg_id)
        obj_certi.write(cr, uid, [data.id], {'legalization_ids': [(6, 0, leg_ids)]})
        list_leglization.append(doss)
    return {'leg_created': str(leg_create) , 'leg_rejected': str(leg_reject) , 'leg_rej_reason': leg_rej_reason, 'leg_ids' : list_leglization }

class create_legalization(wizard.interface):
    def _open_leg(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','cci_missions_legalization_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr, uid, model_data_ids,fields=['res_id'])[0]['res_id']
        val = {
            'domain': "[('dossier_id','in', ["+','.join(map(str, data['form']['leg_ids']))+"])]",
            'name': 'Legalization',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'cci_missions.legalization',
            'views': [(False, 'tree'), (resource_id, 'form')],
            'type': 'ir.actions.act_window'
            }
        return val

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' ,   'arch' : introform,
                    'fields' : introfields,
                    'state' : [('end', 'Cancel'), ('next','Create')]}

        },
        'next': {
            'actions' : [_create_legalization],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end', 'Ok'), ('open','Open Legalization')]}
        },
        'open': {
            'actions': [],
            'result': {'type': 'action', 'action': _open_leg, 'state': 'end'}
        }
    }

create_legalization("cci_mission.create_legalization")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
