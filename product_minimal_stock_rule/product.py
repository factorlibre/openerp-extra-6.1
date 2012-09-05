# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-2011 ToolPart Team LLC (<http://toolpart.hu>).
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

from osv import osv
from osv import fields
from tools.translate import _

class product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'stock_rule_ids': fields.one2many('stock.warehouse.orderpoint', 'product_id', 'Minimal Stock Rules', ),
    }

    def create(self, cr, uid, data, context={}):
        new_id = super(product, self).create(cr, uid, data, context)
        if data.has_key('type') and data['type'] == 'product' and data.has_key('procure_method') and data['procure_method'] == 'make_to_stock':
            rules_obj = self.pool.get('stock.warehouse.orderpoint')
            rule_data = {
                'product_id': new_id,
                'warehouse_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'warehouse0')[1],
                'product_min_qty': 0,
                'product_max_qty': 0,
                'qty_multiple': 1
            }

            v = rules_obj.onchange_product_id(cr, uid, [], rule_data['product_id'], context)
            if v.has_key('value'):
                rule_data.update(v['value'])
            v = rules_obj.onchange_warehouse_id(cr, uid, [], rule_data['warehouse_id'], context)
            if v.has_key('value'):
                rule_data.update(v['value'])
            rules_obj.create(cr, uid, rule_data, context)
        return new_id

product()

