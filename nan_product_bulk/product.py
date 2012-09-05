# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2009 Àngel Àlvarez - NaN  (http://www.nan-tic.com) All Rights Reserved.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import osv, fields
import pooler

from tools import config
from tools.translate import _

class product_product(osv.osv):
    _inherit = 'product.product'
    _name = 'product.product'

    def rounding(self,f, r):
        if not r:
            return f
        return round(f / r) * r

    def _search_values(self,cr,uid,product_id,bulk_id,context=None):
        result = {'qty':None, 'uom':None }
        bom_ids = self.pool.get('mrp.bom').search(cr,uid,[('product_id','=', product_id)],context=context)
        for bom in self.pool.get('mrp.bom').browse(cr, uid, bom_ids, context=context):
            value = False
            for line in bom.bom_lines:
                if line.product_id.id == bulk_id:
                    value += round(line.product_qty,5)
                    uom_id = line.product_uom.id
                    # break  NOTE: I remove break because I found more than one bom with same components more than one time.
                    result['qty'] = round( value, 5 )
                    result['uom'] = uom_id
        return result

    def _get_qty_available( self, cr, uid, ids, field_name, field_value, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context):
            #search stock of this product
            if field_name == 'bulk_qty_available':
                product_stock_qty = product.qty_available
            else:
                product_stock_qty = product.virtual_available

            #search stock of bulk 
            #--------------------
            bulk_stock = 0.0

            for product_bulk in product.bulk_of_product_ids:
                #search unit_convertion       
                factor = 0.0

                #seach bom factor and uom_dest
                res = self._search_values(cr,uid,product_bulk.id, product.id,context=context)
                factor = res['qty']
                uom_dest = res['uom']

                #search stock and uom of bulk
                #for bulk_product in self.browse(cr, uid, [product_bulk.id], context=context):
                if field_name == 'bulk_qty_available':
                    bulk_qty = product_bulk.qty_available
                else:
                    bulk_qty = product_bulk.virtual_available
                uom_id = product.uom_id.id
                
                #convert bulk stock to Udm of this product
                amount = self.pool.get('product.uom')._compute_qty(cr, uid, uom_dest, factor, uom_id)
                if factor > 0.0:
                    bulk_stock += amount * bulk_qty

            #sumatory of stocks
            result[product.id] = self.rounding(product_stock_qty + bulk_stock, product.uom_id.rounding)

        return result

    def _bulk( self, cr, uid, ids, field_name, field_value, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context):
            if product.bulk_of_product_ids and len(product.bulk_of_product_ids) > 0:
                result[product.id] = True
            else:
                result[product.id] = False
        return result

    _columns = {
        'bulk_id': fields.many2one('product.product', 'Bulk', select=1, help='Bulk related with this product'),
        'bulk_of_product_ids': fields.one2many('product.product', 'bulk_id', 'Bulk Of', help='List of all products that have the current one as a bulk.'),
        'bulk': fields.function(_bulk, method=True, type='boolean', string='Is Bulk?', help='A product is a bulk if there are products that have this as bulk.'),
        'bulk_qty_available': fields.function(_get_qty_available, method=True, type='float', string='Bulk Stock'),
        'bulk_virtual_available': fields.function(_get_qty_available, method=True, type='float', string='Virt. bulk stock'),

    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
