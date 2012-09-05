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

form = """<?xml version="1.0"?>
<form string="Add product line">
    <field name="product_id"/>
</form>
"""
fields = {
    'product_id': {'string':'Product', 'type':'many2one', 'required':True, 'relation':'product.product'},
}

def _createlines(self, cr, uid, data, context={}):
    pool_obj = pooler.get_pool(cr.dbname)
    sale_taxes = []
    product = pool_obj.get('product.product').browse(cr, uid, data['form']['product_id'], context)
    if product.taxes_id:
        map(lambda x: sale_taxes.append(x.id), product.taxes_id)
    a =  product.product_tmpl_id.property_account_income.id or False
    if not a:
        a = product.categ_id.property_account_income_categ.id

    value = {
         'product_id': data['form']['product_id'] or False,
         'name': product.name,
         'quantity': 1,
         'uos_id': product.uom_id.id or False,
         'price_unit': product.list_price or 0.0,
         'dossier_product_line_id': data['id'],
         'taxes_id': [(6, 0, sale_taxes)],
         'account_id':a
             }
    id = pool_obj.get('product.lines').create(cr, uid, value, context=context)
    return {}

class add_product_line(wizard.interface):

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type': 'form' ,   'arch': form,'fields': fields,'state': [('end','Cancel'), ('next','Add')]}
        },
        'next': {
            'actions': [_createlines],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

add_product_line("mission.product_line")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: