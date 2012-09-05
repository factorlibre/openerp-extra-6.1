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

xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)

xmlrpc_out = etl.component.output.xmlrpc_out(xmlrpc_conn)
fileconnector_partner=etl.connector.localfile('input/partner.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')

log2=etl.component.transform.logger(name='File')

tran=etl.transition(csv_in1,xmlrpc_out)
tran=etl.transition(xmlrpc_out,log2)
job1=etl.job([log2])

job1.run()
