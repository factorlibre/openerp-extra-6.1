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

from etl.component import component
from etl.connector import connector
from datetime import datetime
import time
import getpass

user = raw_input('Enter gmail username: ')
user = user + '@gmail.com'
password = getpass.unix_getpass("Enter your password:")
cal_conn=etl.connector.gcalendar_connector(user, password)
cal_service = cal_conn.open()
gcalendar_in_events= etl.component.input.gcalendar_in(cal_conn,datetime_format='%Y-%m-%d %H:%M:%S',timezone='Asia/Calcutta',name='Get user events')

#log1=etl.component.transform.logger(name='After write')
#log=etl.component.transform.logger(name='After map')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='event_')",
    'name': "main.get('name','anonymous')",
#    'date_begin':"main.get(datetime.datetime.fromtimestamp(time.mktime(time.strptime('date_begin','%Y-%m-%dT%H:%M:%S.000Z'))).strftime('%Y-%m-%d %H:%M:%S')) ",
#    'date_end':"main.get(datetime.datetime.fromtimestamp(time.mktime(time.strptime('date_end','%Y-%m-%dT%H:%M:%S.000Z'))).strftime('%Y-%m-%d %H:%M:%S'))",

    'date_begin':"main.get('date_begin') ",
    'date_end':"main.get('date_end')",


    'product_id':"main.get('product_id', 'Advance Product')",
}})


ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'trunk_mra', 'admin', 'admin', con_type='xmlrpc')

oo_out_event= etl.component.output.openobject_out(
     ooconnector,
     'event.event',
     { 'id':'id', 'name':'name', 'date_begin':'date_begin', 'date_end':'date_end','product_id':'product_id'
        })

tran=etl.transition(gcalendar_in_events, map)
tran=etl.transition(map, oo_out_event)
job1=etl.job([gcalendar_in_events,oo_out_event])
job1.run()
