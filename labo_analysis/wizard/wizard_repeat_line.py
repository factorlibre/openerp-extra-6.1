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

import wizard
import netsvc
import pooler

take_form = """<?xml version="1.0"?>
<form title="Confirm">
    <separator string="Repeat lines" colspan="4"/>
    <newline/>
</form>
"""

take_fields = {
#    'confirm_en': {'string':'Catalog Number', 'type':'integer'},
}
def _repeat_line(self,cr,uid,data,context={}):
    res={}
    pool = pooler.get_pool(cr.dbname)
#    pool.get('labo.sample').write(cr,uid,data['ids'],{'sample_id':True})
    return {}

class repeate_line_of_request(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {
                    'type' : 'form',
                    'arch' : take_form,
                    'fields' : take_fields,
                    'state' : [('end', 'Cancel'),('repeat', 'Repeat ')]}
        },
            'repeat' : {
            'actions' : [_repeat_line],
            'result' : {'type' : 'state', 'state' : 'end'}
        },
}
repeate_line_of_request('request.line.repeat')
