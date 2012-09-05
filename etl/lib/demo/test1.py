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

fileconnector_partner=etl.connector.localfile('input/partner.csv')

fileconnector_partner1=etl.connector.localfile('input/partner1.csv')
fileconnector_partner3=etl.connector.localfile('input/partner3.csv')
fileconnector_output=etl.connector.localfile('output/test1_partner.csv','w+')

csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
csv_in2= etl.component.input.csv_in(fileconnector_partner1,name='Partner Data1')
csv_out1= etl.component.output.csv_out(fileconnector_output,name='Partner OUT Data1')
sort1=etl.component.transform.sort('name')
log1=etl.component.transform.logger(name='Read Partner File')
log2=etl.component.transform.logger(name='After Sort')
sleep1=etl.component.control.sleep()

tran=etl.transition(csv_in1,sort1)
tran1=etl.transition(csv_in2,sort1)
tran4=etl.transition(sort1,sleep1)
tran4=etl.transition(sleep1,log2)
#tran6=etl.etl.transition(sleep1,log1,channel_source="statistics")
tran5=etl.transition(sort1,csv_out1)


job1=etl.job([csv_in1,csv_in2,csv_out1,sort1,log1,log2,sleep1])

job2 = job1.copy()
job2.run()

