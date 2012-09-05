# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2009 GnuThink Software All Rights Reserved
#    info@gnuthink.com
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

from osv import osv, fields

class ProductCategory(osv.osv):
    _inherit = 'product.category'

    _columns = {
        'taxes_id': fields.many2many('account.tax', 'categ_product_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),
        'supplier_taxes_id': fields.many2many('account.tax',
            'categ_product_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),        
        }

ProductCategory()


class AccountInvoice(osv.osv):

    _inherit = 'account.invoice.line'
    
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', \
                          type='out_invoice', partner_id=False, \
                          fposition_id=False, price_unit=False, \
                          address_invoice_id=False, currency_id=False, context=None):
        if context is None:
            context = {}
        company_id = context.get('company_id',False)
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {'categ_id': False}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0, 'categ_id': False}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if company_id:
            property_obj = self.pool.get('ir.property')
            account_obj = self.pool.get('account.account')
            in_pro_id = property_obj.search(cr, uid, [('name','=','property_account_income'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
            if not in_pro_id:
                in_pro_id = property_obj.search(cr, uid, [('name','=','property_account_income_categ'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])
            exp_pro_id = property_obj.search(cr, uid, [('name','=','property_account_expense'),('res_id','=','product.template,'+str(res.product_tmpl_id.id)+''),('company_id','=',company_id)])
            if not exp_pro_id:
                exp_pro_id = property_obj.search(cr, uid, [('name','=','property_account_expense_categ'),('res_id','=','product.template,'+str(res.categ_id.id)+''),('company_id','=',company_id)])

            if not in_pro_id:
                in_acc = res.product_tmpl_id.property_account_income
                in_acc_cate = res.categ_id.property_account_income_categ
                if in_acc:
                    app_acc_in = in_acc
                else:
                    app_acc_in = in_acc_cate
            else:
                # Get the fields from the ir.property record
                my_value = property_obj.read(cr,uid,in_pro_id,['name','value_reference','res_id'])
                # Parse the value_reference field to get the ID of the account.account record
                account_id = int (my_value[0]["value_reference"].split(",")[1])
                # Use the ID of the account.account record in the browse for the account.account record
                app_acc_in = account_obj.browse(cr, uid, account_id, context=context)
            if not exp_pro_id:
                ex_acc = res.product_tmpl_id.property_account_expense
                ex_acc_cate = res.categ_id.property_account_expense_categ
                if ex_acc:
                    app_acc_exp = ex_acc
                else:
                    app_acc_exp = ex_acc_cate
            else:
                app_acc_exp = account_obj.browse(cr, uid, exp_pro_id, context=context)[0]
            if not in_pro_id and not exp_pro_id:
                in_acc = res.product_tmpl_id.property_account_income
                in_acc_cate = res.categ_id.property_account_income_categ
                ex_acc = res.product_tmpl_id.property_account_expense
                ex_acc_cate = res.categ_id.property_account_expense_categ
                if in_acc or ex_acc:
                    app_acc_in = in_acc
                    app_acc_exp = ex_acc
                else:
                    app_acc_in = in_acc_cate
                    app_acc_exp = ex_acc_cate
            if app_acc_in and app_acc_in.company_id.id != company_id and app_acc_exp and app_acc_exp.company_id.id != company_id:
                in_res_id = account_obj.search(cr, uid, [('name','=',app_acc_in.name),('company_id','=',company_id)])
                exp_res_id = account_obj.search(cr, uid, [('name','=',app_acc_exp.name),('company_id','=',company_id)])
                if not in_res_id and not exp_res_id:
                    raise osv.except_osv(_('Configuration Error !'),
                        _('Can not find account chart for this company, Please Create account.'))
                in_obj_acc = account_obj.browse(cr, uid, in_res_id, context=context)
                exp_obj_acc = account_obj.browse(cr, uid, exp_res_id, context=context)
                if in_acc or ex_acc:
                    res.product_tmpl_id.property_account_income = in_obj_acc[0]
                    res.product_tmpl_id.property_account_expense = exp_obj_acc[0]
                else:
                    res.categ_id.property_account_income_categ = in_obj_acc[0]
                    res.categ_id.property_account_expense_categ = exp_obj_acc[0]

        if type in ('out_invoice','out_refund'):
            a = res.product_tmpl_id.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.product_tmpl_id.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a
        #taxes
        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or res.categ_id.taxes_id and res.categ_id.taxes_id or \
                    (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or res.categ_id.supplier_taxes_id and res.categ_id.supplier_taxes_id or \
                    (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        domain = {}
        result['uos_id'] = res.uom_id.id or uom or False
        result['note'] = res.description
        if result['uos_id']:
            res2 = res.uom_id.category_id.id
            if res2:
                domain = {'uos_id':[('category_id','=',res2 )]}

        result['categ_id'] = res.categ_id.id
        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if uom:
            uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if res.uom_id.category_id.id == uom.category_id.id:
                new_price = res_final['value']['price_unit'] * uom.factor_inv
                res_final['value']['price_unit'] = new_price
        return res_final

AccountInvoice()
