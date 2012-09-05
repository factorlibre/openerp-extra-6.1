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

import wizard
import pooler

class wizard_manage_job_batch(wizard.interface):

    new_batch = '''<?xml version="1.0"?>
    <form string="Create Jobs Batch">
        <field name="name" colspan="4" width="150"/>
    </form>'''
    
    add_batch = '''<?xml version="1.0"?>
    <form string="Add jobs to Batch">
        <field name="job_batch_id" colspan="4" />
    </form>'''
    
    message_form = '''<?xml version="1.0"?>
    <form string="Manage Jobs Batch">
        <field name="message" nolabel="1" colspan="4" width="300"/>
    </form>'''
        
    def _new_batch(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        if 'name' in  data['form']:
            batch_id = pool.get('dm.campaign.document.job.batch').create(cr, uid, {'name':data['form']['name']})
            message = 'New batch is created and job is successfully added to the batch'
        else:    
            message = 'Job is successfully added to the batch'
            batch_id = data['form']['job_batch_id']
        vals = {'campaign_document_job_ids': [[4, data['id']]]}
        pool.get('dm.campaign.document.job.batch').write(cr, uid, batch_id, vals)
        return {'message':message}
    
    batch_fields = {
        'job_batch_id': {'string': 'Job Batch', 'type': 'many2one', 
                   'relation': 'dm.campaign.document.job.batch', 'required': True}
        }
    
    new_batch_fields = {
        'name': {'string': 'Batch Name', 'type': 'char', 'size':64, 'required':True }
        }    

    message_fields = {
        'message': {'string': 'Message', 'type': 'text', 'readonly':True }
        }
        
    def _init_message(self, cr, uid, data, context):
        return {'message':'Using this wizard you can manage your document through different Job batch'}
        
    states = {
        'init': {
            'actions': [_init_message],
            'result': {'type':'form', 'arch':message_form, 'fields':message_fields, 
                       'state':[('end','Cancel'), 
                                ('new_batch','Create Jobs Batch'), 
                                ('add_in_batch','Add jobs to Batch'),]}
            },
        'new_batch': {
            'actions': [],
            'result': {'type': 'form', 'arch': new_batch, 
                       'fields': new_batch_fields, 
                       'state':[('message','Create Batch')]}
            },
        'add_in_batch': {
            'actions': [],
            'result': {'type': 'form', 'arch': add_batch, 'fields': batch_fields,
                       'state':[('message','Add In Batch')]}
        },
        
        'message': {
            'actions': [_new_batch],
            'result': {'type': 'form', 'arch': message_form, 'fields': message_fields,
                       'state': [('end', 'Ok', 'gtk-ok', True)]}
        },        
        }
wizard_manage_job_batch("wizard_manage_job_batch")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
