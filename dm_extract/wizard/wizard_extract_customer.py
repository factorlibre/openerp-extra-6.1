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
import pooler
    
parameter_form = '''<?xml version="1.0"?>
<form string="Customers Extraction">
    <field name="name" colspan="4" width="125"/>
    <field name="code" colspan="4"/>
</form>'''

parameter_fields = {
    'name': {'string': 'Customer File Name', 'type': 'char', 'required': True},
    'code': {'string': 'Customer File Code', 'type': 'char', 'required': True}
    }


message_fields = {
    'number_pa': {'string': 'Number of customers extracted', 'type': 'integer', 'readonly': True},
    }

_form = """<?xml version="1.0"?>
<form string="Extract Customers">
    <field name="number_pa" colspan="4"/>
</form>
"""
def action_extract_customer(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    sql_query = pool.get('dm.address.segmentation').browse(cr,uid,data['id']).sql_query
    cr.execute(sql_query)
    pa_ids = map(lambda x: x[0] ,cr.fetchall())
    pool.get('dm.customers_file').create(cr,uid,{'name':data['form']['name'],
                                            'code':data['form']['code'],
                                            'address_ids': [[6, 0, pa_ids]],
                                             'segmentation_id':data['id']})
    data['form']['number_pa'] = len(pa_ids)
    return data['form']
    


class wizard_extract_customer(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': parameter_form, 
                       'fields': parameter_fields, 
                       'state': [('end', 'Cancel'), ('ok', 'Ok')]}

        },
        'ok': {
            'actions': [action_extract_customer],
            'result': {
                'type': 'form', 'arch': _form, 
                'fields': message_fields,
                'state': [('end', 'Ok')]
            }
        },
    }
wizard_extract_customer("wizard.extract.customer")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
