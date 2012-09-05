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
import netsvc
from osv import osv, fields

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    def wkf_approve_order(self, cr, uid, ids):
        res = super(purchase_order,self).wkf_approve_order(cr, uid, ids)
        for po in self.browse(cr, uid, ids):
            part_id = po.partner_id.id
            cids = self.pool.get('res.company').search(cr, uid, [('partner_id','=',part_id)])
            if cids:
                sale_obj = self.pool.get('sale.order')
                sale_line_obj = self.pool.get('sale.order.line')
                partner_obj = self.pool.get('res.partner')

                shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id', '=', cids[0])])

                if shop_ids:
                    shop_id = shop_ids[0]
                    new_ids = []

                    user = self.pool.get('res.users').browse(cr, uid, uid)
                    partner_id = user.company_id.partner_id.id
                    partner_addr = partner_obj.address_get(cr, uid, [partner_id],
                            ['invoice', 'delivery', 'contact'])
                    default_pricelist = partner_obj.browse(cr, uid, partner_id,
                                {}).property_product_pricelist.id
                    fpos = partner_obj.browse(cr, uid, partner_id,
                                {}).property_account_position
                    fpos_id = fpos and fpos.id or False
                    vals = {
                        'origin': 'PO:%s' % str(po.name),
                        'picking_policy': 'direct',
                        'shop_id': shop_id,
                        'partner_id': partner_id,
                        'pricelist_id': default_pricelist,
                        'partner_invoice_id': partner_addr['invoice'],
                        'partner_order_id': partner_addr['contact'],
                        'partner_shipping_id': partner_addr['delivery'],
                        'order_policy': 'manual',
                        'date_order': time.strftime('%Y-%m-%d'),
                        'order_policy': po.invoice_method=='picking' and 'picking' or 'manual',
                        'fiscal_position': fpos_id
                    }
                    new_id = sale_obj.create(cr, uid, vals)
                    fpos = user.company_id.partner_id.property_account_position and user.company_id.partner_id.property_account_position.id or False
                    for line in po.order_line:
                        value = {}
                        if line.product_id:
                            value = sale_line_obj.product_id_change(cr, uid, [], default_pricelist,
                                    line.product_id.id, qty=line.product_qty, partner_id=partner_id, fiscal_position=fpos)['value']
                            value['product_id'] = line.product_id.id
                            value['product_uos'] = value.get('product_uos', False)
                        value['name'] = line.name
                        value['price_unit'] = line.price_unit
                        value['product_uom'] = line.product_uom.id
                        value['product_uom_qty'] = line.product_qty
                        value['order_id'] = new_id
                        sale_line_obj.create(cr, uid, value)
        return res
purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

