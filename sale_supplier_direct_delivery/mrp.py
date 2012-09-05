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

from osv import fields, osv

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    
    _columns = {
        #Field that is used temporarily: in the sale.action_ship_create method, the procurement is created but isn't yet linked back to the 
        #sale_order_line. So when the procurement itself generate a purchase order, we can't find back the sale order line yet.
        #Instead, we set the procurement.related_direct_delivery_purchase_order once the procurement created the purchase order
        #so later on, back in sale.py, once the procurement is linked back to the sale order line, we can find back the crate purchase order, sigh! 
        'related_direct_delivery_purchase_order': fields.many2one('purchase.order', 'Related Direct Delivery Purchase Order'),
    }

    def action_po_assign(self, cr, uid, ids, context={}):
        po_id = super(procurement_order, self).action_po_assign(cr, uid, ids, context)

        for procurement in self.browse(cr, uid, ids):#TODO ensure that works!!! Why only one po_id is returned from super method?
            if procurement.move_id.sale_line_id.is_supplier_direct_delivery:
                customer_location_id = self.pool.get('purchase.order').browse(cr, uid, po_id).partner_id.property_stock_customer.id
                self.pool.get('purchase.order').write(cr, uid, po_id, {'location_id':  customer_location_id})

            self.pool.get('procurement.order').write(cr, uid, procurement.id, {'related_direct_delivery_purchase_order': po_id})

procurement_order()
