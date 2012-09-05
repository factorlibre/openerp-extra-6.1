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
import tempfile
import netsvc
import base64
from osv import osv

email_send_form = '''<?xml version="1.0" encoding="utf-8"?>
	<form string="Send purchase order by Email">
		<field name="partner_address_id"/>	
		<field name="smtp_server_id"/>
		<newline/>
		<field name="subject"/>
		<newline/>
		<separator string="Message:" colspan="4"/>
		<field name="content" nolabel="1" colspan="4"/>
	</form>'''

email_send_fields = {
    'smtp_server_id': {'string':"Smtp Server",
                     'type':'many2one',
                      'relation':'email.smtpclient',
                       'required':True,
                       },
    'subject': {'string':'Subject',
                 'type':'char', 
                 'size':64,
                'required':True,
                },
    'content': {'string':'Content', 
                'type':'text_tag',
                'required':True,
                },
	'partner_address_id': {'string':"Send Email to",
				'type':'many2one',
				'relation':'res.partner.address',
				'required':True,
				},
}



email_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send purchase order by Email" >
	<field name="email_sent" nolabel="1" colspan="4" width = '400'/>
</form>'''


email_done_fields = {
    'email_sent': {'string':'Emails sent', 'type':'char', 'size':256, 'readonly': True},
}

def _get_defaults(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    
    po_obj = pool.get('purchase.order').browse(cr, uid, data['id'], context)
    
    smtp_server_id = pool.get('email.smtpclient').search(cr, uid, [('active','=',True),('state','=','confirm')], context=False)
    smtp_server_id = smtp_server_id and smtp_server_id[0] or False
    
    return {'smtp_server_id': smtp_server_id,
    		'subject':po_obj.name,
    		'content':po_obj.partner_address_id.supp_email_content or '',
    		'partner_address_id' : po_obj.partner_address_id.id
    		}

def _send_mails(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	po_id = data['id']
	attachment_ids = pool.get('ir.attachment').search(cr, uid, 
											[('res_model', '=', 'purchase.order'),
											('res_id', '=', po_id)])
	attachments = []
	attach_name = []
	for attach in pool.get('ir.attachment').browse(cr, uid, attachment_ids):
		f_name = tempfile.gettempdir() +'/'+ attach.name 
		open(f_name,'wb').write(base64.decodestring(attach.datas))
		attachments.append(f_name)
		attach_name.append(attach.name)
		
	po_state = pool.get('purchase.order').browse(cr, uid, po_id).state
	if po_state == 'cancel' :
		raise osv.except_osv(_('Error sending email'), _('You can not send email when order is cancelled'))
	
	report_name = {'draft' : 'purchase.quotation',
					'confirmed' : 'purchase.order',
					'approved' : 'purchase.order',}
#	report_id = pool.get('ir.actions.report.xml').search(cr, uid, 
#								[('model', '=', 'purchase.order'),
#								 ('internal_name' ,'=', report_name[po_state])])
								 
#	report_obj = pool.get('ir.actions.report.xml').browse(cr, uid, report_id)
#	if report_obj : 
#		if report_obj.attachment_use and attachment:
#			name = 
		
	service = netsvc.LocalService("report."+report_name[po_state]);
	(result, format) = service.create(cr, uid, [po_id], {}, context)
	
	f_name = tempfile.gettempdir() +'/purchase_order.' + format
	open(f_name,'wb').write(result)	
	attachments.append(f_name)
	
	pa_obj = pool.get('res.partner.address')
	email_to = [pa_obj.browse(cr, uid, data['form']['partner_address_id']).email]
	state = pool.get('email.smtpclient').send_email(cr, uid, 
										data['form']['smtp_server_id'], 
										email_to, data['form']['subject'], 
										data['form']['content'], attachments)
	if not state:
		msg_string = 'Please check the Server Configuration!'
	else :
		msg_string = 'Email is send at %s successfully'%email_to[0]
	return {'email_sent':msg_string}

class po_send_email(wizard.interface):

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_send_mails],
            'result': {'type': 'form', 'arch': email_done_form, 'fields': email_done_fields, 'state': [('end','Ok'),]  }
        }
    }
po_send_email('purchase.order.email_send')
