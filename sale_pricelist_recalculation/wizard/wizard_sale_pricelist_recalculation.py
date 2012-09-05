# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from osv import osv, fields
from tools.translate import _

class sale_extended_wizard(osv.osv_memory):
    _name = "sale.extended.wizard"
    _description = "Wizard On Sale Order which lets you change pricelist runtime"
    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, domain=[('type','=','sale')])
    }

    def change_pricelist_products(self, cr, uid, ids, context):
        obj_curr = self.browse(cr, uid, ids, context)[0]
        order_line_obj = self.pool.get('sale.order.line')
        sale_order_pool = self.pool.get('sale.order')
        pricelist_id = obj_curr['pricelist_id']
        sale_obj = sale_order_pool.browse(cr, uid, context['active_id'], context)
        partner_id = sale_obj.partner_id.id
        date_order = sale_obj.date_order

        if sale_obj.pricelist_id.id == pricelist_id.id:
            raise osv.except_osv(_('Warning'),_('The Pricelist is already applied to the sales order!'))

        if sale_obj['state'] == 'draft':
            sale_order_pool.write(cr, uid, context['active_id'], {'pricelist_id': pricelist_id.id})
            for line in sale_obj.order_line:
                vals = order_line_obj.product_id_change(cr, uid, line.id, pricelist_id.id, line.product_id.id ,qty=line.product_uom_qty,uom=line.product_uom.id,uos=line.product_uos.id, partner_id=partner_id, date_order=date_order)
                if vals.get('value',False):
                    if 'price_unit' in vals['value'].keys():
                        order_line_obj.write(cr, uid, line.id, {'price_unit': vals['value']['price_unit']},context=context)
        else:
            raise osv.except_osv(_('Warning'),_('PriceList cannot be changed! Make sure the Sales Order is in "Quotation" state!'))
        return {'type': 'ir.actions.act_window_close'}

sale_extended_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: