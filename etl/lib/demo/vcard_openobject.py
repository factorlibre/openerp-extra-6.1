#!/usr/bin/python
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
import sys
sys.path.append('..')

import etl

filevcard = etl.connector.localfile('input/contacts.vcf')
vcard_in1 = etl.component.input.vcard_in(filevcard)
ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin', 'admin', con_type='xmlrpc')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('org', 'anonymous'), prefix='partner_')",
    'address_id': "tools.uniq_id(main.get('fn', 'anonymous'), prefix='contact_')",
    'name': "main.get('org',['anonymous'])[0]",
    'contact_name': "main.get('fn','anonymous')",
    'email': "main.get('email','').upper()"
}})

oo_out= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name'}
)

oo_out2= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.address',
     {'name': 'contact_name', 'id':'address_id', 'partner_id:id':'id','email':'email'}
)
log1=etl.component.transform.logger(name='vCard->Oo')

tran=etl.transition(vcard_in1,map)
tran=etl.transition(map,log1)
tran=etl.transition(log1,oo_out)
tran=etl.transition(oo_out,oo_out2)

log2=etl.component.transform.logger(name='Count')

count = etl.component.control.data_count()
tran=etl.transition(map, count, channel_destination='gmail')
tran=etl.transition(oo_out, count, channel_destination='partner')
tran=etl.transition(oo_out2, count, channel_destination='address')
tran=etl.transition(count, log2)


job1=etl.job([vcard_in1,oo_out,oo_out2, log2,count])
job1.run()
