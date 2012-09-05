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
import etl

ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin', 'a', con_type='xmlrpc')
map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('org', 'anonymous'), prefix='partner_')",
    'address_id': "tools.uniq_id(main.get('fn', 'anonymous'), prefix='contact_')",
    'name': "main.get('org',['anonymous'])[0]",
    'contact_name': "main.get('fn','anonymous')",
    'email': "main.get('email','').upper()"
}})

oo_out= etl.component.output.openobject_out_create(
     ooconnector,
     'res.partner',
     {'name':'name'}
)



tran=etl.transition(map,oo_out)
job1=etl.job([map,oo_out])
xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)
xmlrpc_in= etl.component.input.xmlrpc_in_block(xmlrpc_conn, job1)
job2=etl.job([xmlrpc_in])
job2.run()
