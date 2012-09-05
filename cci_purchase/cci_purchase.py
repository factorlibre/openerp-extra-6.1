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
import time

import netsvc
from osv import fields, osv

class purchase_order_history(osv.osv):
    _name = 'purchase.order.history'
    _decription = 'purchase order'
    _rec_name = 'date'
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'PO Ref'),
        'date': fields.date('Modification Date'),
        'user_id': fields.many2one('res.users', 'User')
    }
purchase_order_history()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _decription = 'purchase order'
    _columns = {
        'history_ids': fields.one2many('purchase.order.history','purchase_id', 'PO Ref'),
    }
    def wkf_temp_order0(self, cr, uid, ids, context={}):
        for po in self.browse(cr, uid, ids):
            self.write(cr, uid, [po.id], {'state' : 'wait_approve'})
        return True

    def button_purchase_temp(self, cr, uid, ids, context={}):
        wf_service = netsvc.LocalService('workflow')
        for po in self.browse(cr, uid, ids):
            if po.amount_total < 10000:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_confirm', cr)
            else:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_tempo', cr)
        return True

    def action_invoice_create(self, cr, uid, ids, *args):
        res = False
        journal_obj = self.pool.get('account.journal')
        for o in self.browse(cr, uid, ids):
            il = []
            for ol in o.order_line:

                if ol.product_id:
                    a = ol.product_id.product_tmpl_id.property_account_expense.id
                    if not a:
                        a = ol.product_id.categ_id.property_account_expense_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'), _('There is no expense account defined for this product: "%s" (id:%d)') % (ol.product_id.name, ol.product_id.id,))
                else:
                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category')
                fpos = o.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                il.append(self.inv_line_create(cr, uid, a, ol))

            a = o.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase')], limit=1)
            inv = {
                #'name': o.partner_ref or o.name,
                'reference': "P%dPO%d" % (o.partner_id.id, o.id),
                'account_id': a,
                'type': 'in_invoice',
                'partner_id': o.partner_id.id,
                'currency_id': o.pricelist_id.currency_id.id,
                'address_invoice_id': o.partner_address_id.id,
                'address_contact_id': o.partner_address_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'origin': o.name,
                'invoice_line': il,
                'fiscal_position': o.partner_id.property_account_position.id,
                'payment_term':o.partner_id.property_payment_term and o.partner_id.property_payment_term.id or False,
                'internal_note': o.internal_notes,
            }
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'in_invoice','from_purchase':True})
            self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'in_invoice'}, set_total=True)

            self.write(cr, uid, [o.id], {'invoice_id': inv_id})
            res = inv_id
        return res

    def write(self, cr, uid, ids, vals, context=None):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
#    def wkf_write_approvator(self, cr, uid, ids, context={}):
#        wf_service = netsvc.LocalService('workflow')
#        for po in self.browse(cr, uid, ids):
#            self.write(cr, uid, [po.id], { 'validator' : uid})
#            wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_dummy_confirmed', cr)
#        return True

    def wkf_create_purchase_history(self, cr, uid, ids, context={}):
        history_obj = self.pool.get('purchase.order.history')
        for id in ids:
            history_obj.create(cr, uid, {'purchase_id':id, 'date': time.strftime('%Y-%m-%d'), 'user_id':uid})
        return True

    def wkf_confirm_order(self, cr, uid, ids, context={}):
        for po in self.browse(cr, uid, ids):
            if self.pool.get('res.partner.event.type').check(cr, uid, 'purchase_open'):
                self.pool.get('res.partner.event').create(cr, uid, {'name':'Purchase Order: '+po.name, 'partner_id':po.partner_id.id, 'date':time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id':uid, 'partner_type':'retailer', 'probability': 1.0, 'planned_cost':po.amount_untaxed})
        current_name = self.name_get(cr, uid, ids)[0][1]
        for id in ids:
            self.write(cr, uid, [id], {'state': 'confirmed','validator': uid, 'approvator': uid}) #'approvator' : uid
        return True

    _columns = {
        'internal_notes': fields.text('Internal Note'),
        'approvator' : fields.many2one('res.users', 'Approved by', readonly=True),
        'state': fields.selection([('draft', 'Request for Quotation'), ('wait', 'Waiting'), ('confirmed', 'Confirmed'),('wait_approve','Waiting For Approve'), ('approved', 'Approved'),('except_picking', 'Shipping Exception'), ('except_invoice', 'Invoice Exception'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Order State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
                }
purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
