# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
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
############################################################################################

from osv import fields,osv
from tools.translate import _

import re

FIELD_FILTER = ['property']

class product_attributes_wizard(osv.osv_memory):
    _name = 'product.attributes.wizard'

    _columns = {
        'field': fields.many2one('ir.model.fields','Field', help="Select your field to copy", 
            domain=[
                ('ttype','not in',FIELD_FILTER),
                '|',
                ('model','=','product.product'),
                ('model','=','product.template'),
            ],
            required=True,
        ),
        'product_to': fields.many2one('product.product','Product TO', help="Select your product to copy", required=True),
        'lang': fields.many2one('res.lang','Language', help="Select language to copy", required=True),
        'result': fields.text('Result', readonly=True),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
    }

    def copy_attributes(self, cr, uid, ids, data, context={}):
        """Copy attributes to field"""

        form = self.browse(cr, uid, ids[0])
        field = form.field
        product_to = form.product_to

        context['lang'] = form.lang.code

        if len(data['active_ids']) > 1:
            raise osv.except_osv(_('Error!'), _('This wizard is available only one product'))

        for prod in data['active_ids']:
            value = self.pool.get('product.product').read(cr, uid, [prod], [field.name], context)
            values = {field.name: value[0][field.name]}

            self.pool.get('product.product').write(cr, uid, [product_to.id], values, context)

        values = {
            'state':'done',
            'result': _('%s copy to: %s - %s') % (data['active_ids'], product_to.id, field.name),
        }
        self.write(cr, uid, ids, values)

        return True

product_attributes_wizard()

class product_attributes_fields_wizard(osv.osv_memory):
    _name = 'product.attributes.fields.wizard'

    _columns = {
    }

    _defaults = {
    }

    def open_attribute_fields(self, cr, uid, ids, data, context={}):
        """Open Product Form with Attribute fields"""

        if len(data['active_ids']) > 1:
            raise osv.except_osv(_('Error!'), _('This wizard is available only one product'))

        form = self.browse(cr, uid, ids[0])
        products = data['active_ids']

        product = self.pool.get('product.product').browse(cr, uid, products[0], context)

        if not product.attribute_group_id:
            raise osv.except_osv(_('Error !'), _('Select a attribute group!.'))

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
            
        mod_id = mod_obj.search(cr, uid, [('name', '=', 'product_normal_action')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','in',[product.id])]
        act_win['context'] = {'attribute_group_id':1}
        act_win['name'] = "%s" % (product.name)

        return act_win

product_attributes_fields_wizard()
