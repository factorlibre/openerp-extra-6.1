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

sugarcrm_conn=etl.connector.sugarcrm_connector('admin','sugarpasswd',url='http://192.168.0.7/sugarcrm/soap.php')
sugarcrm_in1= etl.component.input.sugarcrm_in(sugarcrm_conn,'Contacts')

log=etl.component.transform.logger(name='After map')




tran=etl.transition(sugarcrm_in1,log,channel_source='Contacts')

job1=etl.job([sugarcrm_in1,log])
job1.run()
print job1.get_statitic_info()
#
## sugarcrm -> logger
##facebook -> mapping -> schema_valodator   -> openobject_out ('main')
##                                          -> logger1 ('invalid_field')
##                                                               -> logger2 invalid_name
##                                                               -> logger3 invalid_key
#                                                               -> logger4 invalid_null
#                                                               -> logger5 invalid_type
#                                                               -> logger6 invalid_size
#                                                               -> logger7 invalid_format












