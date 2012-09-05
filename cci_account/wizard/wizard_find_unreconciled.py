# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import netsvc
import wizard
from osv import osv
import pooler
from tools.translate import _

_inv_form = '''<?xml version="1.0"?>
<form string="Product to find">
    <field name="product_id"/>
</form>'''

def _period_get(self, cr, uid, datas, ctx={}):
    try:
        pool = pooler.get_pool(cr.dbname)
        ids = pool.get('account.period').find(cr, uid, context=ctx)
        return {'period_id': ids[0]}
    except:
        return {}

_inv_fields = {
    'product_id': {'string':'Product', 'type':'many2one', 'relation':'product.product', 'required':True},
}

def _action_open_window(self, cr, uid, data, context):
    form = data['form']
    invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')
    inv_line_obj = pooler.get_pool(cr.dbname).get('account.invoice.line')
    cr.execute("select distinct ai.id from account_invoice ai Inner join account_invoice_line al on al.invoice_id=ai.id and al.product_id = %s and ai.reconciled is null", (form['product_id'],))
    return {
        'domain': [('id', 'in', cr.fetchall() )],
        'name': "Unreconciled Invoices",
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.invoice',
        'type': 'ir.actions.act_window'
    }

class wiz_find_inv(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_inv_form, 'fields':_inv_fields, 'state':[('end','Cancel'),('find','Find Invoices')]}
        },
        'find': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
        }
    }
wiz_find_inv('account.invoice.find')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

