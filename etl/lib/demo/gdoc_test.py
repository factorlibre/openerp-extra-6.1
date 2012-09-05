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



gdoc_connector = etl.connector.gdoc_connector(user,password) # gmail
gdoc_in1= etl.component.input.gdoc_in(gdoc_connector, file_path='/home/tiny/Desktop/')

#fileconnector_partner=etl.connector.localfile('/home/tiny/Desktop/partner1.csv')

fileconnector_output=etl.connector.localfile('output/gdoc.csv','r+')

#csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
csv_out1= etl.component.output.csv_out(fileconnector_output,name='Partner OUT Data1')
log1=etl.component.transform.logger(name='Read Partner File')

tran=etl.transition(gdoc_in1, log1)
#tran=etl.transition(log1, csv_in1)
tran1=etl.transition(log1, csv_out1)

job1=etl.job([gdoc_in1,csv_out1], name="dd")

job1.run()