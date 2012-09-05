# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Gábor Dukai <gdukai@gmail.com>
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

from osv import osv, fields

class label_wizard_product(osv.osv_memory):
    _name = 'label.wizard.product'

    def _default_template_id(self, cr, uid, context):
        tmpl_ids = self.pool.get('label.templates')\
            .search(cr, uid, [('model_int_name','=','product.product')])
        try:
            return tmpl_ids[0]
        except IndexError:
            return False

    _columns = {
        'template_id': fields.many2one('label.templates', 'Label Template',
            required=True, domain=[('model_int_name','=','product.product')]),
        'line_ids': fields.one2many('label.wizard.product.line', 'wizard_id',
            'Items'),
    }

    _defaults = {
        'template_id': _default_template_id,
    }

    def action_print(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0])
        obj_list = []
        for line in wiz.line_ids:
            obj_list.append({'id': line.product_id.id, 'qty': line.quantity})
        return {
                'context'  : {
                    'template_id': wiz.template_id.id,
                    'obj_list': obj_list},
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'label.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

label_wizard_product()

class label_wizard_product_line(osv.osv_memory):
    _name = 'label.wizard.product.line'

    _columns = {
        'wizard_id': fields.many2one('label.wizard.product', 'Wizard',
            required=True),
        'product_id' : fields.many2one('product.product', 'Product',
            required=True),
        'quantity': fields.integer('Qty', required=True),

    }

    _defaults = {
        'quantity': lambda *a: 1,
    }

label_wizard_product_line()