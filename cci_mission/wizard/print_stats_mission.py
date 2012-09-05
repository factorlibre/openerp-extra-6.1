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
import time

import wizard
import pooler

form = """<?xml version="1.0"?>
<form string="Print Stats per mission type">
    <field name="date1"/>
    <field name="date2"/>
</form>"""

fields = {
      'date1': {'string':'Date from', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-01')},
      'date2': {'string':'Date to', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
   }

class print_stats_mission(wizard.interface):
    def _checkint(self, cr, uid, data, context):
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','_Cancel'),('print','P_rint')]},
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'stats.mission.type', 'state':'end'},
        },
    }

print_stats_mission('stats.mission.type')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: