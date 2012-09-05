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
import threading
import sys
sys.path.append('..')

import etl

#this demo file shows how to design jobs when you want 
#to load data of many2many tables into OpenERP.

#Note that the csv files are the same as if you wished 
#to import them in a module.


#definition of the csv inputs
fileconnector_groups=etl.connector.localfile('input/res.groups.csv')
fileconnector_users=etl.connector.localfile('input/res.users.csv')
csv_in_groups= etl.component.input.csv_in(fileconnector_groups,name='Groups Data')
csv_in_users= etl.component.input.csv_in(fileconnector_users,name='Users Data')

#logger definition
log1=etl.component.transform.logger(name='Processed Data')

#definition of the openobject outputs
ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'etl', 'admin', 'admin', con_type='xmlrpc')
oo_out_groups = etl.component.output.openobject_out(
     ooconnector,
     'res.groups',
     {'id':'id','name':'name'}
            )
oo_out_users = etl.component.output.openobject_out(
     ooconnector,
     'res.users',
     {'id':'user_id','name':'user_name', 'login':'login','context_lang':'context_lang','groups_id:id':'groups_id:id'}
            )

#definition of the map component, for the user data
map_keys = {'main':{
    'user_id': "tools.uniq_id(main.get('login', 'anonymous'), prefix='user_')",
    'user_name': "main.get('name', 'anonymous')",
    'login': "main.get('login', 'anonymous')",
    'context_lang': "main.get('context_lang','en_US')",
    'groups_id:id': "main.get('groups_id:id','False')",
}}
map = etl.component.transform.map(map_keys)


sqlconnector_partner=etl.connector.sql_connector('localhost',5432, 'etl', 'qdp', 'qdp')

sql_in1= etl.component.transform.sql_join(
    sqlconnector_partner,"select res_id from ir_model_data where name = '%s'",'user_id',outputkey='unique_res_id')


#definition of the transitions
tran0=etl.transition(csv_in_groups, oo_out_groups)
tran1=etl.transition(csv_in_users, map)
tran2=etl.transition(map, oo_out_users)
tran3=etl.transition(oo_out_users, sql_in1)
tran4=etl.transition(sql_in1, log1)



job1=etl.job([oo_out_groups,oo_out_users,log1])
#print job1
job1.run()
#print job1.get_statitic_info()
