p#!/usr/bin/python
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
import threading
import sys
sys.path.append('..')

import etl

fileconnector_partner=etl.connector.localfile('input/partner_cat.csv')
fileconnector_partner=etl.connector.localfile('input/category.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
csv_in2= etl.component.input.csv_in(fileconnector_partner,name='category Data')

log1=etl.component.transform.logger(name='Read Partner File')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='partner_')",
    'name': "main.get('pname','anonymous')",
    'ref': "main.get('code','anonymous')",
    'category_id': "main.get('category_id','False')",


    'category_id_main': "tools.uniq_id(main.get('cat_name', 'anonymous'), prefix='cat_')",
    'category_name':"main.get('cat_name',['anonymous'])",
}})

ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'etl', 'admin', 'admin', con_type='xmlrpc')

oo_out_cat= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.category',
     {'id':'category_id_main','name':'category_name'}
            )

oo_out_partner= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name', 'category_id:id':'category_id_main', 'ref':'ref'}
            )

tran=etl.transition(csv_in1, log1)
tran=etl.transition(log1, csv_in2)
#tran=etl.transition(log1,csv_in2)
tran=etl.transition(csv_in2, map)

tran=etl.transition(map, oo_out_cat)
tran=etl.transition(map, oo_out_partner)
#tran=etl.transition(facebook_in_events, map2)
##,channel_source='friends'
#tran=etl.transition(facebook_in_friends, log)
#tran=etl.transition(map, oo_out_partner)
#tran=etl.transition(map, oo_out_address)
#tran=etl.transition(map, oo_out_address1)
#tran=etl.transition(map1, oo_out_event)
#tran=etl.transition(map1, oo_out_event1)
#tran=etl.transition(oo_out_address,log1)
job1=etl.job([map,log1,oo_out_cat,oo_out_partner])
job1.run()
