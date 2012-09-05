# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import time
import netsvc
from osv import fields, osv
import ir
from decimal import Decimal

class pos_order(osv.osv):
    _inherit = "pos.order"
    def action_invoice(self, cr, uid, ids, context={}):
        res_obj = self.pool.get('res.company')
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        inv_ids = []
        if self.browse(cr,uid,ids)[0].price_type=='tax_excluded':
            return super(pos_order, self).action_invoice(cr, uid, ids, context)
        for order in self.browse(cr, uid, ids, context):
            curr_c = order.user_id1.company_id
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue
            if not order.partner_id:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))
            cr.execute('select a.id from account_account a, res_company p where p.account_receivable=a.id and p.id=%s', (curr_c.id, ))
            res=cr.fetchone()
            acc=res and res[0] or None
            seq_obj=self.pool.get('ir.sequence')
            inv = {
                'name': seq_obj.get(cr,uid,'account.invoice.in_invoice'),
                'origin': order.name,
                'account_id':acc,
                'journal_id':order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'price_type': 'tax_included'
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = order.partner_id.id, fposition_id=order.partner_id.property_account_position.id)['value'])
                inv_line['price_unit'] = line.price_unit
                inv_line['price_subtotal'] = line.price_subtotal
                inv_line['discount'] = line.discount
                inv_line['account_id'] = acc
                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context)

        for i in inv_ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', i, 'invoice_open', cr)
        return inv_ids

    def _amount_tax(self, cr, uid, ids, field_name, arg, context):
        res = {}
        product_taxes = []
        tax_obj = self.pool.get('account.tax')
        for order in self.browse(cr, uid, ids):
            val = 0.0
            for line in order.lines:
                if order.partner_id and order.partner_id.property_account_position and order.partner_id.property_account_position.tax_ids:
                    tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, order.partner_id.property_account_position, line.product_id.taxes_id)
                    product_taxes = self.pool.get('account.tax').browse(cr, uid,tax_id)
                else:
                    product_taxes = line.product_id.taxes_id

                if order.price_type == 'tax_included':
                    val = reduce(lambda x, y: x+round(y['amount'], 2),
                            tax_obj.compute_inv(cr, uid, product_taxes,
                                line.price_unit* \
                                (1-(line.discount or 0.0)/100.0),line.qty),
                                val)
                else:
                    val = reduce(lambda x, y: x+round(y['amount'], 2),
                            tax_obj.compute(cr, uid, product_taxes,
                                line.price_unit* \
                                (1-(line.discount or 0.0)/100.0),line.qty),
                                val)
            res[order.id] = val
        return res

    def _amount_total(self, cr, uid, ids, field_name, arg, context):
        id_set = ",".join(map(str, ids))
        cr.execute("""
                    SELECT p.id,
                          COALESCE(SUM(l.price_subtotal)::decimal(16,2), 0) AS amount
                    FROM pos_order as p
                    LEFT JOIN pos_order_line as l ON l.order_id = p.id
                    WHERE p.id IN (""" + id_set  +""") GROUP BY p.id """)
        res = dict(cr.fetchall())
        for rec in self.browse(cr, uid, ids, context):
            if rec.partner_id \
               and rec.partner_id.property_account_position \
               and rec.partner_id.property_account_position.tax_ids:
                res[rec.id] = res[rec.id] - rec.amount_tax
            else :
                res[rec.id] = res[rec.id] + rec.amount_tax
        return res


    _columns = {
        'price_type': fields.selection([
            ('tax_included','Tax included'),
            ('tax_excluded','Tax excluded')
        ], 'Price method', required=True),
        'amount_total': fields.function(_amount_total, method=True,
            string='Total'),
        'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
    }
    _defaults = {
        'price_type': lambda *a: 'tax_included',
    }

    def add_product(self, cr, uid, order_id, product_id, qty, context=None):
        res = super(pos_order, self).add_product(cr, uid, order_id, product_id, qty, context)
        sql = """ select id from pos_order_line where order_id = %d """%(order_id)
        cr.execute(sql)
        for line in self.pool.get('pos.order.line').browse(cr, uid,[x[0] for x in cr.fetchall()]):
            _tax = 0.0
            _with_tax_subtotal = 0.0
            _without_tax_subtotal = 0.0
            if line.qty <> 0.0:
                _with_tax_subtotal = line.price_unit*line.qty
                if line.product_id.taxes_id:
                    _tax = reduce(lambda x,
                                  y: x+round(y['amount'], 2),
                                  self.pool.get('account.tax').compute_inv(cr,
                                                                         uid,
                                                                         line.product_id.taxes_id,
                                                                         line.price_unit,line.qty),_tax)
                    _without_tax_subtotal = (line.price_unit*line.qty) - _tax
                else :
                    _without_tax_subtotal = _with_tax_subtotal
                self.pool.get('pos.order.line').write(cr, uid, [line.id], {
                    'price_subtotal': _without_tax_subtotal,
                    'price_subtotal_incl':  _with_tax_subtotal
                    })
            else :
                self.pool.get('pos.order.line').write(cr, uid, [line.id], {
                    'price_subtotal': _without_tax_subtotal,
                    'price_subtotal_incl':  _with_tax_subtotal
                    })
        return res

    def onchange_partner_pricelist(self, cr, uid, ids, part,context={}):
        res = super(pos_order, self).onchange_partner_pricelist(cr, uid, part, context)
        for order in self.browse(cr,uid,ids):
            for line in order.lines:
                res = self.pool.get('pos.order.line').amount_compute(cr,uid, [line.id], line.price_ded,line.discount,line.price_unit,order.pricelist_id.id,line.product_id.id,line.qty, order.price_type,part,context)
                self.write(cr,uid,ids,{'lines':[(1,line.id,{'price_subtotal': 0.0, 'price_subtotal_incl': 0.0})]})
        return res
    def write(self, cr, user, ids, values, context={}):
        if 'partner_id' in values:
            for order in self.browse(cr,user,ids):
                for line in order.lines:
                    result = self.pool.get('pos.order.line').onchange_amount(cr,user, [line.id], line.price_ded,line.discount,line.price_unit,order.pricelist_id.id,line.product_id.id,line.qty, order.price_type,order.partner_id.id,context)
                    values.update({'lines':[(1,line.id,{'price_subtotal':result['value']['price_subtotal']})]})
        return super(pos_order,self).write(cr, user, ids, values, context)
    def create_account_move(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_period_obj = self.pool.get('account.period')
        account_tax_obj = self.pool.get('account.tax')
        period = account_period_obj.find(cr, uid, context=context)[0]

        for order in self.browse(cr, uid, ids, context=context):
            curr_c = self.pool.get('res.users').browse(cr, uid, uid).company_id
            comp_id = self.pool.get('res.users').browse(cr, order.user_id.id, order.user_id.id).company_id
            comp_id=comp_id and comp_id.id or False
            to_reconcile = []
            group_tax = {}
            account_def = self.pool.get('ir.property').get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
            order_account = order.partner_id and order.partner_id.property_account_receivable and order.partner_id.property_account_receivable.id or account_def or curr_c.account_receivable.id

            # Create an entry for the sale
            move_id = account_move_obj.create(cr, uid, {
                'journal_id': order.sale_journal.id,
                'period_id': period,
                }, context=context)

            # Create an move for each order line
            for line in order.lines:

                tax_amount = 0
                taxes = [t for t in line.product_id.taxes_id]
                if  order.partner_id and order.partner_id.property_account_position.tax_ids:
                    tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, order.partner_id.property_account_position, taxes)
                    product_taxes = self.pool.get('account.tax').browse(cr, uid,tax_ids)
                    computed_taxes = account_tax_obj.compute_inv(cr, uid, product_taxes, line.price_unit, line.qty)
                elif order.price_type=='tax_included':
                    computed_taxes = account_tax_obj.compute_inv(
                        cr, uid, taxes, line.price_unit, line.qty)
                else:
                    computed_taxes = account_tax_obj.compute(
                        cr, uid, taxes, line.price_unit, line.qty)

                for tax in computed_taxes:
                    tax_amount += round(tax['amount'], 2)
                    group_key = (tax['tax_code_id'],
                                tax['base_code_id'],
                                tax['account_collected_id'])

                    if group_key in group_tax:
                        group_tax[group_key] += round(tax['amount'], 2)
                    else:
                        group_tax[group_key] = round(tax['amount'], 2)

                amount = line.price_subtotal
                # Search for the income account
                if  line.product_id.property_account_income.id:
                    income_account = line.\
                                    product_id.property_account_income.id
                elif line.product_id.categ_id.\
                        property_account_income_categ.id:
                    income_account = line.product_id.categ_id.\
                                    property_account_income_categ.id
                else:
                    raise osv.except_osv(_('Error !'), _('There is no income '\
                        'account defined for this product: "%s" (id:%d)') \
                        % (line.product_id.name, line.product_id.id, ))


                # Empty the tax list as long as there is no tax code:
                tax_code_id = False
                tax_amount = 0
                while computed_taxes:
                    tax = computed_taxes.pop(0)
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    # If there is one we stop
                    if tax_code_id:
                        break

                # Create a move for the line
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.contract_number or order.name,
                    'quantity': line.qty,
                    'product_id':line.product_id.id,
                    'move_id': move_id,
                    'account_id': income_account,
                    'company_id': comp_id,
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': tax_code_id,
                    'tax_amount': tax_amount,
                }, context=context)

                # For each remaining tax with a code, whe create a move line
                for tax in computed_taxes:
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    if not tax_code_id:
                        continue

                    account_move_line_obj.create(cr, uid, {
                        'name': order.name,
                        'date': order.date_order,
                        'ref': order.contract_number or order.name,
                        'product_id':line.product_id.id,
                        'quantity': line.qty,
                        'move_id': move_id,
                        'account_id': income_account,
                        'company_id': comp_id,
                        'credit': 0.0,
                        'debit': 0.0,
                        'journal_id': order.sale_journal.id,
                        'period_id': period,
                        'tax_code_id': tax_code_id,
                        'tax_amount': tax_amount,
                    }, context=context)


            # Create a move for each tax group
            (tax_code_pos, base_code_pos, account_pos)= (0, 1, 2)
            for key, amount in group_tax.items():
                account_move_line_obj.create(cr, uid, {
                    'name':order.name,
                    'date': order.date_order,
                    'ref': order.contract_number or order.name,
                    'move_id': move_id,
                    'company_id': comp_id,
                    'quantity': line.qty,
                    'product_id':line.product_id.id,
                    'account_id': key[account_pos],
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': key[tax_code_pos],
                    'tax_amount': amount,
                }, context=context)

            # counterpart
            to_reconcile.append(account_move_line_obj.create(cr, uid, {
                'name': order.name,
                'date': order.date_order,
                'ref': order.contract_number or order.name,
                'move_id': move_id,
                'company_id': comp_id,
                'account_id': order_account,
                'credit': ((order.amount_total<0) and -order.amount_total)\
                    or 0.0,
                'debit': ((order.amount_total>0) and order.amount_total)\
                    or 0.0,
                'journal_id': order.sale_journal.id,
                'period_id': period,
            }, context=context))


            # search the account receivable for the payments:
            account_receivable = order.sale_journal.default_credit_account_id.id
            if not account_receivable:
                raise  osv.except_osv(_('Error !'),
                    _('There is no receivable account defined for this journal:'\
                    ' "%s" (id:%d)') % (order.sale_journal.name, order.sale_journal.id, ))
            am=0.0
            for payment in order.statement_ids:
                am+=payment.amount

                if am > 0:
                    payment_account = \
                        payment.statement_id.journal_id.default_debit_account_id.id
                else:
                    payment_account = \
                        payment.statement_id.journal_id.default_credit_account_id.id

                # Create one entry for the payment
                if payment.is_acc:
                    continue
                payment_move_id = account_move_obj.create(cr, uid, {
                    'journal_id': payment.statement_id.journal_id.id,
                    'period_id': period,
                }, context=context)

            for stat_l in order.statement_ids:
                if stat_l.is_acc and len(stat_l.move_ids):
                    for st in stat_l.move_ids:
                        for s in st.line_id:
                            if s.credit:
                                account_move_line_obj.copy(cr, uid, s.id, { 'debit': s.credit,
                                                                            'statement_id': False,
                                                                            'credit': s.debit})
                                account_move_line_obj.copy(cr, uid, s.id, {
                                                                        'statement_id': False,
                                                                        'account_id':order_account
                                                                     })
            self.write(cr,uid,order.id,{'state':'done'})
        return True
pos_order()

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"


    def create(self, cr, user, vals, context={}):
        if vals.get('product_id'):
            price_unit = [prod.lst_price for prod in \
                          self.pool.get('product.product').browse(cr, \
                          user, [vals['product_id']])][0]
            vals.update({'price_unit': price_unit})
            return super(pos_order_line, self).create(cr, user, vals, context)
        return False

#    def onchange_qty(self, cr, uid, ids, pricelist, product_id, qty, p, partner_id=False):
#        price = self.price_by_product(cr, uid, ids, pricelist, product_id, qty, partner_id)
#        res = self._amount_line2(cr, uid, ids,[],[],  context={})
#        if ids:
#            for line in self.browse(cr,uid,ids):
#                return {'value': {'discount':line.discount,
#                                  'price_ded':line.price_unit*qty*line.discount*0.01,
#                                  'price_subtotal': (res['price_subtotal'] - line.price_unit*qty*line.discount*0.01),
#                                  'price_subtotal_incl':(res['price_subtotal_incl'] - line.price_unit*qty*line.discount*0.01)}}
#        else :
#            return {'value': {'discount':0.0,'notice':'No Discount','price_ded':0.0,'price_subtotal': res['price_subtotal'],'price_subtotal_incl':res['price_subtotal_incl']}}
#
#    def onchange_product_id(self, cr, uid, ids, pricelist, product_id, tax_type, qty=0, partner_id=False):
#        res = super(pos_order_line, self).onchange_product_id(cr, uid, ids, pricelist, product_id, qty, partner_id)
#        res['value'].update(self.onchange_qty(cr, uid, ids, pricelist, product_id, qty, tax_type, partner_id)['value'])
#        return res

    def onchange_amount(self, cr,uid, ids, price_ded,discount,price_unit,pricelist_id,product_id,qty, price_type,partner_id,context={}):
        res={}
        return {'value': self.amount_compute(cr,uid, ids, price_ded,discount,price_unit,pricelist_id,product_id,qty, price_type,partner_id,context)}

    def _amount_line1(self, cr, uid,ids,price_unit,qty,pricelist_id,product_id,partner_id, discount,price_ded, context):
        res = {'subtotal':0.0,'discount':0.0,'price_ded':0.0}
        res['price_ded']=price_ded
        if price_ded!=0.0 and context not in ('discount','qty'):#or not discount:
            discount = (price_ded*100)/ (price_unit*qty)
        if discount!=0.0:
            res['subtotal'] = price_unit * qty * (1 - (discount or 0.0) / 100.0)
        else:
            res['subtotal']=price_unit*qty
        if context=='qty':
            res['price_ded']=(price_unit*qty)-res['subtotal']
        res['discount']=discount or 0.0
        return res

    def amount_compute(self, cr,uid, ids, price_ded,discount,price_unit,pricelist_id,product_id,qty, price_type,partner_id,context):
        res = {}
        tax_obj = self.pool.get('account.tax')
        res_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        res_company = self.pool.get('res.company')
        price_subtotal= price_subtotal_incl=0.0
        res={
            'price_subtotal': 0.0,
            'price_ded':0.0,
            'price_unit': 0.0,
            'price_subtotal_incl': 0.0,
            'data': []
        }
        res_init=0.0
        if not product_id:
            return res
        if product_id:
            price = super(pos_order_line,self).price_by_product(cr, uid, ids, pricelist_id, product_id, qty, partner_id)
            res['price_unit']=price
        if res_init==0.0:
            res_init = self._amount_line1(cr, uid, ids, price,qty,pricelist_id,product_id,partner_id,discount,price_ded, context)['subtotal']
            disc = self._amount_line1(cr, uid, ids, price,qty,pricelist_id,product_id,partner_id,discount,price_ded, context)['discount']
            price_ded = self._amount_line1(cr, uid, ids, price,qty,pricelist_id,product_id,partner_id,discount,price_ded, context)['price_ded']
        res['price_ded']=price_ded
        product_taxes = []
        product_id=product_id and self.pool.get('product.product').browse(cr,uid,product_id)
        if product_id:
            product_taxes = filter(lambda x: x.price_include, product_id.taxes_id)
        if partner_id:
            partner_id=partner_obj.browse(cr,uid,partner_id)
        taxes = []
        if partner_id and partner_id.property_account_position and partner_id.property_account_position.tax_ids:
            tax_struct = dict([(item.tax_src_id.id, item.tax_src_id.amount)
                                      for item in partner_id.property_account_position.tax_ids]
                                  + \
                                  [(item.tax_dest_id.id, item.tax_dest_id.amount)
                                      for item in partner_id.property_account_position.tax_ids])

            tax_map_by_fiscal_position = [(item.tax_src_id.id, item.tax_dest_id.id) for item in partner_id.property_account_position.tax_ids]

            for tax in product_id.taxes_id:
                tax_src_amount = tax_struct.get(tax.id, None)
                tax_dest_amount = tax_struct.get(dict(tax_map_by_fiscal_position).get(tax.id, None), None)
                if tax_dest_amount is not None and Decimal(str(tax_dest_amount)) == 0:
                    taxes.append(tax)
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, partner_id.property_account_position, taxes)
                product_taxes = self.pool.get('account.tax').browse(cr, uid,tax_ids)
                inverse_compute_tax_res = tax_obj.compute_inv(cr, uid, taxes, res['price_subtotal_incl'], qty)
                if inverse_compute_tax_res:
                    res['price_subtotal_incl'] = inverse_compute_tax_res[0]['price_unit']
                    res['price_subtotal'] = res['price_subtotal_incl']

        if ((set(product_taxes) == set(product_id and product_id.taxes_id)) or not product_taxes) and (price_type == 'tax_excluded'):
            res['price_subtotal_incl'] = res_init
            res['price_subtotal'] = res_init 
            if partner_id and partner_id.property_account_position and partner_id.property_account_position.tax_ids:
              for tax in tax_obj.compute(cr, uid, product_taxes, res['price_subtotal']/qty, qty):
                  res['price_subtotal_incl'] = res['price_subtotal_incl'] + tax['amount']
            else:
              for tax in tax_obj.compute(cr, uid, product_id.taxes_id, res['price_subtotal']/qty, qty):
                  res['price_subtotal_incl'] = res['price_subtotal_incl'] + tax['amount']
        else:
            res['price_subtotal'] = res['price_subtotal_incl']=res_init
            if partner_id and partner_id.property_account_position and partner_id.property_account_position.tax_ids:
                for tax in tax_obj.compute_inv(cr, uid, product_taxes, res['price_subtotal_incl']/qty, qty):
                    res['price_subtotal'] = res['price_subtotal'] - tax['amount']
            else:
                for tax in tax_obj.compute_inv(cr, uid, product_id.taxes_id, res['price_subtotal_incl']/qty, qty):
                    res['price_subtotal'] = res['price_subtotal'] - tax['amount']
        if price_subtotal==0.0:
            price_subtotal=res['price_subtotal']
        if price_subtotal_incl==0.0:
            price_subtotal_incl=res['price_subtotal_incl']
        comp = res_obj.browse(cr,uid,uid).company_id.company_discount or 0.0
        if context=='price_ded':
            res.update({'notice':'no discount',
                    'discount' : disc,
        })
            if discount > comp:
                res.update({'notice':''})
        if context=='discount':
            res.update({'discount':discount,
                            'price_ded':price*qty*discount*0.01 or 0.0})
            if discount > comp :
                res.update({'notice':''})
            else:
                res.update({'notice':'Minimum Discount',})
        res['price_subtotal']= round(res['price_subtotal'], 2)
        res['price_subtotal_incl']= round(res['price_subtotal_incl'], 2)

        return res


    def _amount_line2(self, cr, uid, ids, name, args, context={}):

        """
        Return the subtotal excluding taxes with respect to price_type.
        """
        res = {}
        tax_obj = self.pool.get('account.tax')
        res_init = super(pos_order_line, self)._amount_line(cr, uid, ids, name, args, context)
        for line in self.browse(cr, uid, ids):
            res[line.id] = self.amount_compute(cr,uid,ids, line.price_ded,line.discount,line.price_unit,line.order_id.pricelist_id and line.order_id.pricelist_id.id or False,line.product_id and line.product_id.id or False,line.qty, line.order_id.price_type,line.order_id and line.order_id.partner_id and line.order_id.partner_id.id or False, False)
        return res

   #         {
   #             'price_subtotal': 0.0,
   #             'price_subtotal_incl': 0.0,
   #             'data': []
   #         }
   #         if not line.qty:
   #             continue
   #         if line.order_id:
   #             product_taxes = []
   #             if line.product_id:
   #                 product_taxes = filter(lambda x: x.price_include, line.product_id.taxes_id)
   #             if ((set(product_taxes) == set(line.product_id.taxes_id)) or not product_taxes) and (line.order_id.price_type == 'tax_included'):
   #                 res[line.id]['price_subtotal_incl'] = res_init[line.id]
   #             else:
   #                 res[line.id]['price_subtotal'] = res_init[line.id]
   #                 for tax in tax_obj.compute_inv(cr, uid, product_taxes, res_init[line.id]/line.qty, line.qty):
   #                     res[line.id]['price_subtotal'] = res[line.id]['price_subtotal'] - round(tax['amount'], 2)
   #         else:
   #             res[line.id]['price_subtotal'] = res_init[line.id]
   #         if res[line.id]['price_subtotal']:
   #             res[line.id]['price_subtotal_incl'] = res[line.id]['price_subtotal']
   #             for tax in tax_obj.compute(cr, uid, line.product_id.taxes_id, res[line.id]['price_subtotal']/line.qty, line.qty):
   #                 res[line.id]['price_subtotal_incl'] = res[line.id]['price_subtotal_incl'] + tax['amount']
   #                 res[line.id]['data'].append( tax)
   #         else:
   #             res[line.id]['price_subtotal'] = res[line.id]['price_subtotal_incl']
   #             for tax in tax_obj.compute_inv(cr, uid, line.product_id.taxes_id, res[line.id]['price_subtotal_incl']/line.qty, line.qty):
   #                 res[line.id]['price_subtotal'] = res[line.id]['price_subtotal'] - tax['amount']
   #                 res[line.id]['data'].append( tax)
   #         res[line.id]['price_subtotal']= round(res[line.id]['price_subtotal'], 2)
   #         res[line.id]['price_subtotal_incl']= round(res[line.id]['price_subtotal_incl'], 2)
   #     return res

    def _get_order(self, cr, uid, ids, context):
        result = {}
        for inv in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            for line in inv.lines:
                result[line.id] = True
        return result.keys()
    _columns = {
        'price_subtotal': fields.function(_amount_line2, method=True, string='Subtotal w/o tax', multi='amount',
            store={'pos.order':(_get_order,['price_type'],-2), 'pos.order.line': (lambda self,cr,uid,ids,c={}: ids, None,-2)}),
        'price_subtotal_incl': fields.function(_amount_line2, method=True, string='Subtotal', multi='amount',
            store={'pos.order':(_get_order,['price_type'],-2), 'pos.order.line': (lambda self,cr,uid,ids,c={}: ids, None,-2)}),
    }


pos_order_line()

