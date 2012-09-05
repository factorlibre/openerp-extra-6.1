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
import time
import datetime

extract_form = '''<?xml version="1.0"?>
<form string="Customers Extraction">
    <field name="name" colspan="4" width="200"/>
    <field name="code" colspan="4"/>
</form>'''

extract_fields = {
    'name': {'string': 'Customer File Name', 'type': 'char', 'required': True, 'size': 64},
    'code': {'string': 'Customer File Code', 'type': 'char', 'required': True, 'size': 64}
    }

def _get_details(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    seg_obj = pool.get('dm.campaign.proposition.segment').browse(cr, uid, data['id'])
    cur_time = time.strftime('%Y-%m-%d')
    custo_name = seg_obj.name + ' ' + cur_time
    custo_code = seg_obj.code and (seg_obj.code + ' ' + cur_time) or cur_time
    vals = {'name': custo_name, 'code': custo_code}
    return vals

def action_force_extraction(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    seg_obj = pool.get('dm.campaign.proposition.segment').browse(cr, uid, data['id'])
    if seg_obj.segmentation_id:
        cr.execute(seg_obj.segmentation_id.sql_query)
        address_ids = map(lambda x: x[0], cr.fetchall())
    else:
        address_ids = []
    use_census = seg_obj.use_census
    cur_time = time.strftime('%Y-%m-%d')
    if use_census:
        start_census = seg_obj.start_census
        end_census = seg_obj.end_census
        type_census = seg_obj.type_census
        t = time.strptime(cur_time, '%Y-%m-%d')
        d = datetime.datetime(t[0], t[1], t[2])
        if type_census == 'months':
            diff = end_census - start_census
            start_date = (d - datetime.timedelta(diff*365/12)).date()
        else:
            kwargs = {type_census: end_census-start_census}
            start_date = (d - datetime.timedelta(**kwargs)).date()
        end_date = cur_time
        sale_ids = pool.get('sale.order').search(cr, uid, [('partner_invoice_id', 'in', address_ids), ('date_order', '<', end_date), ('date_order', '>', start_date)])
    address_ids = [sale.partner_invoice_id.id for sale in pool.get('sale.order').browse(cr, uid, sale_ids)]
    pool.get('dm.customers_file').create(cr, uid, {'name': data['form']['name'],
                                            'code': data['form']['code'],
                                            'segmentation_id': seg_obj.segmentation_id.id,
                                            'address_ids': [[6, 0, set(address_ids)]],})
    return {}

class wizard_force_extraction(wizard.interface):
    states = {
        'init': {
            'actions': [_get_details],
            'result': {'type': 'form', 'arch': extract_form, 
                       'fields': extract_fields, 
                       'state': [('end', 'Cancel'), ('ok', 'Ok')]}

        },
        'ok': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': action_force_extraction,
                'state': 'end'
            }
        },
    }
wizard_force_extraction("wizard.force.extraction")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
