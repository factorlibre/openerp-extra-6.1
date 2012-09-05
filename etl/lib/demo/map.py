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

input_part = etl.component.input.data([
    {'id': 1, 'name': 'Fabien', 'country_id': 3},
    {'id': 2, 'name': 'Luc', 'country_id': 3},
    {'id': 3, 'name': 'Henry', 'country_id': 1}
])
input_cty = etl.component.input.data([
    {'id': 1, 'name': 'Belgium'},
    {'id': 3, 'name': 'France'}
])
map_keys = {'main': {
    'id': "main['id']",
    'name': "main['name'].upper()",
    'country': "country_var[main['country_id']]['name']"
}}
def preprocess(self, channels):
    cdict = {}
    for trans in channels['country']:
        for d in trans:
            cdict[d['id']] = d
    return {'country_var': cdict}

map=etl.component.transform.map(map_keys,preprocess)
log=etl.component.transform.logger(name='Read Partner File')

tran=etl.transition(input_part,map, channel_destination='main')
tran1=etl.transition(input_cty,map, channel_destination='country')
tran4=etl.transition(map,log)

job=etl.job([log])
job.run()

