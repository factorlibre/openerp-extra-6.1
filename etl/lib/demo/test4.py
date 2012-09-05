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

sqlconnector_partner=etl.connector.sql_connector('localhost',5432, 'trunk', 'fp', 'fp')

sql_in1= etl.component.input.sql_in(
    sqlconnector_partner,'select * from res_partner where id<=10 order by id')

log1=etl.component.transform.logger(name='Read Partner')


tran=etl.transition(sql_in1,log1)

job1=etl.job([log1])
job1.run()

