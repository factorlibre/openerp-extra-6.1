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

__authors__ = [ 
    "OpenERP S.A.",
    "Borja López Soilán (Pexego) <borjals@pexego.es>"
]

from osv import fields, osv
import decimal_precision as dp

class purchase_order(osv.osv):
    """
    Extends the purchase order to allow using "tax included" prices.
    """
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context):
        """
        Overwrites/extends the amounts calculation to allow tax included prices.
        """
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids):
            if order.price_type == 'tax_included':
                #
                # Use the tax included calculation
                #
                res[order.id] = {
                    'amount_untaxed': 0.0,
                    'amount_tax': 0.0,
                    'amount_total': 0.0,
                }
                val = val1 = 0.0
                cur=order.pricelist_id.currency_id
                for line in order.order_line:
                    for c in self.pool.get('account.tax').compute_inv(cr, uid, line.taxes_id, line.price_unit, line.product_qty, order.partner_address_id.id, line.product_id, order.partner_id):
                        val+= c['amount']
                    val1 += line.price_subtotal
                res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
                res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
                res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            else:
                #
                # Use the default calculation
                #
                res = super(purchase_order, self)._amount_all(cr, uid, ids, field_name, arg, context)
        return res


    def _get_order(self, cr, uid, ids, context={}):
        """
        Returns the orders that must be updated when some order lines change.
        """
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'price_type': fields.selection([
            ('tax_included','Tax included'),
            ('tax_excluded','Tax excluded')
        ], 'Price method', required=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['price_type'], 20),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['price_type'], 20),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['price_type'], 20),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums"),
    }

    _defaults = {
        'price_type': lambda *a: 'tax_excluded',
    }

    def _inv_get(self, cr, uid, order, context={}):
        """
        Returns the columns as a dictionary.
        """
        return {
            'price_type': order.price_type
        }


    def action_invoice_create(self, cr, uid, ids, *args):
        """
        Extend the invoice creation action to set the price type if needed.
        """
        #
        # Count how many orders have tax included prices.
        #
        tax_included_count = 0
        orders = self.browse(cr, uid, ids)
        for order in orders:
            if order.price_type == 'tax_included':
                tax_included_count += 1

        if tax_included_count:
            if len(orders) == tax_included_count:
                #
                # Every order has tax include prices, we must create the invoice
                # and (afterwards) set the price type and recalculate.
                #
                invoice_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, args)
                self.pool.get('account.invoice').write(cr, uid, [invoice_id], { 'price_type': 'tax_included' })
                self.pool.get('account.invoice').button_compute(cr, uid, [invoice_id], {'type': 'in_invoice'}, set_total=True)
            else:
                # We have no current way of creating an invoice mixing
                # tax included and tax excluded prices, so we just fail:
                raise osv.except_osv(_('Error!'), _("You can't mix tax included and tax excluded purchases in one invoice!"))
        else:
            # All the invoices are 'tax excluded', that's the default value
            # so we just let the default method create the invoice.
            invoice_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, args)

        return invoice_id


purchase_order()

class purchase_order_line(osv.osv):
    """
    Extends the purchase order lines to alter the calculation when
    tax includes prices are used.
    """
    _inherit = 'purchase.order.line'

    def _amount_line(self, cr, uid, ids, name, arg, context):
        """
        Calculate the subtotal for the line without taxes.
        """
        # Use the original method to calculate the amounts:
        res = super(purchase_order_line, self)._amount_line(cr, uid, ids, 'price_subtotal', arg, context)
        # Check if we are using 'tax_included' prices:
        if ids and self.browse(cr, uid, ids[0]).order_id.price_type == 'tax_included':
            #
            # Tax included => Remove the taxes from the line amounts.
            #
            cur_facade=self.pool.get('res.currency')
            tax_facade = self.pool.get('account.tax')
            for line in self.browse(cr, uid, ids):
                for tax in tax_facade.compute_inv(cr, uid, line.taxes_id, res[line.id]/line.product_qty, line.product_qty):
                    res[line.id] = res[line.id] - tax['amount']
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_facade.round(cr, uid, cur, res[line.id])
        return res
    
    def _amount_line_incl(self, cr, uid, ids, name, arg, context):
        """
        Calculate the subtotal for the line with taxes.
        """
        # Use the original method to calculate the amounts:
        res = super(purchase_order_line, self)._amount_line(cr, uid, ids, 'price_subtotal', arg, context)
        # Check if we *aren't* using 'tax_included' prices on the subtotal:
        if ids and self.browse(cr, uid, ids[0]).order_id.price_type != 'tax_included':
            #
            # Tax excluded on the subtotal => Add taxes here from the line amounts.
            #
            cur_facade=self.pool.get('res.currency')
            tax_facade = self.pool.get('account.tax')
            for line in self.browse(cr, uid, ids):
                for tax in tax_facade.compute(cr, uid, line.taxes_id, res[line.id]/line.product_qty, line.product_qty):
                    res[line.id] = res[line.id] + tax['amount']
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_facade.round(cr, uid, cur, res[line.id])
        return res


    _columns = {
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal w/o tax', digits_compute=dp.get_precision('Purchase Price')),
        'price_subtotal_incl': fields.function(_amount_line_incl, method=True, string='Subtotal', digits_compute=dp.get_precision('Purchase Price')),
    }
purchase_order_line()

class stock_picking(osv.osv):
    """
    Extends the stock pickings to manage the creation of invoices with
    tax included prices when the original order had tax included prices.
    """
    _inherit = 'stock.picking'
    _description = "Picking list"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                                group=False, type='out_invoice', context=None):
        """
        Extend the invoice creation action to set the price type if needed.
        """
        #
        # Count how many pickings have tax included prices.
        #
        tax_included_count = 0
        lines_count = 0
        pickings = self.browse(cr, uid, ids, context=context)
        for picking in pickings:
            #
            # We must find the orders associated with this picking and check
            # if they have tax included prices.
            # As picking lines may come from different orders (even if it is
            # not the usual), we must check it line by line.
            #
            for move in picking.move_lines:
                if move.purchase_line_id and move.purchase_line_id.order_id:
                    lines_count += 1
                    if move.purchase_line_id.order_id.price_type == 'tax_included':
                        tax_included_count += 1
        
        if tax_included_count:
            if lines_count == tax_included_count:
                #
                # Every order has tax include prices, we must create the invoice
                # and (afterwards) set the price type and recalculate.
                #
                invoices_map = super(stock_picking, self).action_invoice_create(cr,
                                               uid, ids, journal_id=journal_id,
                                               group=group, type=type,
                                               context=context)
                invoice_ids = list(set(invoices_map.values()))
                self.pool.get('account.invoice').write(cr, uid, invoice_ids, { 'price_type': 'tax_included' })
                self.pool.get('account.invoice').button_compute(cr, uid, invoice_ids, {'type': 'in_invoice'}, set_total=True)
            else:
                # We have no current way of creating an invoice mixing
                # tax included and tax excluded prices, so we just fail:
                raise osv.except_osv(_('Error!'), _("You can't mix tax included and tax excluded purchases in one invoice!"))
        else:
            # All the invoices are 'tax excluded', that's the default value
            # so we just let the default method create the invoice.
            invoices_map = super(stock_picking, self).action_invoice_create(cr,
                                            uid, ids, journal_id=journal_id,
                                            group=group, type=type,
                                            context=context)
        return invoices_map

stock_picking()

