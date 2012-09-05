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
import tools
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Send Email from registration">
    <field name="subject"/>
    <newline/>
    <field name="email_from"/>
    <newline/>
    <field name="body" width="500" height="200"/>
</form>
"""
fields = {
  'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
  'email_from': {'string':'Email From', 'type':'char', 'size':32, 'required':True},
  'body': {'string':'Body', 'type':'text', 'required':True},
      }

msg_form = """<?xml version="1.0"?>
<form string="Result">
    <field name="message" width="650" height="200"/>
</form>
"""
msg_fields = {
      'message': {'string':'Result', 'type':'text', 'readonly':True}
      }

def _sendemail(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    mail_from = data['form']['email_from'] or False
    if not mail_from:
        mail_from = pool.get('res.users').browse(cr, uid, [uid], context)[0].address_id.email
    count_reg = 0
    message = ''
    for reg in pool.get('event.registration').browse(cr, uid, data['ids'], context):
        to = reg.email_from or reg.contact_id.email or False
        if to:
            res = tools.email_send(mail_from, [to], data['form']['subject'], data['form']['body'])
            if res:
                count_reg += 1
            else:
                message += '''Error: Mail not sent, Partner %s does not have a valid address mail on Registration ID: %s \n'''%(reg.partner_id.name, reg.id)
        else:
            message += '''Error: Mail not sent, Partner %s does not have a email available on Registration ID: %s \n'''%(reg.partner_id.name, reg.id)
    count_msg = '''%s mails have been successfully sent\n'''%(count_reg)
    message = count_msg + message
    return {'message': message}

class send_email(wizard.interface):
    states = {
        'init' : {
           'actions' : [],
           'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Cancel'), ('send','Send')]}
        },
        'send': {
            'actions': [_sendemail],
            'result': {'type':'form', 'arch': msg_form, 'fields': msg_fields, 'state':[('end','Ok')]}
        },
    }

send_email("event.send_email")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: