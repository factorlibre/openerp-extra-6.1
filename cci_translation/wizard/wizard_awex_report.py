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
import netsvc
import pooler
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Awex Report">
    <field name="date_from"/>
    <newline />
    <field name="date_to"/>
    <newline />
</form>
"""

fields = {
        'date_from': {'string':'From Date', 'type':'date', 'required' : True, 'default': lambda *a: time.strftime('%Y-%m-01')},
        'date_to': {'string':'To Date', 'type':'date', 'required' : True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
        }

class translation_awex_report(wizard.interface):

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','_Cancel'),('open','Open _Report')]}
                    },
        'open': {
            'actions': [],
            'result': {'type':'print', 'report':'translation.awex', 'state':'end'}
                }
            }
translation_awex_report("translation_awex_report")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: