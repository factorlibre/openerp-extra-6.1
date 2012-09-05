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
from osv import fields,osv, orm
import time
import tools

class discount_campaign(osv.osv):
    _name = "discount.campaign"
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_stop': fields.date('Stop Date', required=True),
        'line_ids': fields.one2many('discount.campaign.line','discount_id', 'Discount Lines'),
        'state' : fields.selection([('draft','Draft'),('open','Open'),('cancel','Canceled'),('done','Done')],'State',readonly=True),
        'journal_id': fields.many2one('account.journal', 'Refund Journal', domain="[('type','=','sale_refund')]", required=True),
    }

    _defaults = {
        'state': lambda *args: 'draft'
    }


    def action_open(self, cr, uid, ids, *args):
        return True

    def action_done(self, cr, uid, ids,group=True,type='out_refund', context=None):
        # need to make perfect checking
        # remaining to check sale condition
        # need Improvement
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        
        for campaign in self.browse(cr, uid, ids):
            for rule_line in campaign.line_ids:
                query_params = (campaign.id,campaign.date_start,campaign.date_stop,)
                query_cond = ""
                if rule_line.condition_product_id:
                    query_cond += " AND inv_line.product_id = %s" 
                    query_params += (rule_line.condition_product_id.id,)
                if rule_line.condition_category_id:
                    query_cond += " AND prod_template.categ_id = %s" 
                    query_params += (rule_line.condition_category_id.id,)
                cr.execute("""
                 SELECT max(invoice.id), sum(inv_line.quantity), sum(inv_line.price_subtotal)
                 FROM account_invoice invoice
                  LEFT JOIN res_partner partner ON (invoice.partner_id = partner.id)
                  LEFT JOIN account_invoice_line inv_line ON (invoice.id = inv_line.invoice_id)
                  LEFT JOIN product_product product ON (inv_line.product_id = product.id)
                  LEFT JOIN product_template prod_template ON (product.product_tmpl_id = prod_template.id)
                 WHERE partner.discount_campaign = %s 
                  AND (invoice.date_invoice BETWEEN %s AND %s) 
                  AND invoice.type = 'out_invoice' 
                  AND invoice.state in ('open','paid')
                 """ + query_cond + """
                  GROUP BY partner.id
                """, query_params)
                for res in cr.fetchall():
                    if res[1] >= rule_line.condition_quantity:
                        invoice_record = invoice_obj.browse(cr, uid, res[0], context)
                        new_invoice = {}
                        partner_id = invoice_record.partner_id.id
                        fpos = partner_obj.browse(cr, uid, partner_id).property_account_position
                        new_invoice.update({
                            'partner_id': partner_id,
                            'journal_id': campaign.journal_id.id,
                            'account_id': invoice_record.partner_id.property_account_receivable.id,
                            'address_contact_id': invoice_record.address_contact_id.id,
                            'address_invoice_id': invoice_record.address_invoice_id.id,
                            'type': 'out_refund',
                            'date_invoice': time.strftime('%Y-%m-%d'),
                            'state': 'draft',
                            'number': False,
                            'fiscal_position': fpos and fpos.id or False
                        })
                        invoice_id = invoice_obj.create(cr, uid, new_invoice,context=context)
                        account_id = rule_line.condition_product_id and (rule_line.condition_product_id.property_account_income and rule_line.condition_product_id.property_account_income.id or (rule_line.condition_product_id.categ_id.property_account_income_categ and rule_line.condition_product_id.categ_id.property_account_income_categ.id or False)) or (rule_line.condition_category_id.property_account_income_categ and rule_line.condition_category_id.property_account_income_categ.id or False)
                        if not account_id:
                            account_id = campaign.journal_id.default_debit_account_id and campaign.journal_id.default_debit_account_id.id or False,
                            if not account_id:
                                raise osv.except_osv(_('No account found'),_("OpenERP was not able to find an income account to put on the refund invoice line. Configure the default debit account on the selected refund journal."))
                        invoice_line_id = invoice_line_obj.create(cr, uid,  {
		               'name': rule_line.name,
		               'invoice_id': invoice_id,
		               'product_id': rule_line.condition_product_id and rule_line.condition_product_id.id or False,
		               'uos_id': rule_line.condition_product_id and rule_line.condition_product_id.uom_id.id or False, 
		               'account_id': account_id,
		               'price_unit': res[2] / res[1],
		               'quantity': res[1] * rule_line.discount / 100,
		            }, context=context)
        return True

discount_campaign()

class discount_campaign_line(osv.osv):
    _name = "discount.campaign.line"
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'sequence': fields.integer('Sequence', required=True),
        'condition_sale': fields.char('Sale Condition', size = 60),
        'condition_category_id': fields.many2one('product.category', 'Category'),
        'condition_product_id' : fields.many2one('product.product', 'Product'),
        'condition_quantity' : fields.float('Min. Quantity'),
        'discount' : fields.float('Discount (%)'),
        'discount_id': fields.many2one('discount.campaign', 'Discount Lines'),
    }
    _defaults = {
        'sequence': lambda *a: 5,
    }
    _order = "sequence, condition_quantity desc"
discount_campaign_line()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'discount_campaign': fields.many2one('discount.campaign', 'Discount Campaign'),
    }
res_partner()

#it seems more interessting and work-oriented to have the discount campaign set on the partner (sale order is useless?)
#class sale_order(osv.osv):
#    _inherit = "sale.order"
#    _columns = {
#        'discount_campaign': fields.many2one('discount.campaign', 'Discount Campaign'),
#    }
#
#    def onchange_partner_id(self, cr, uid, ids, part):
#        if not part:
#            return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False, 'payment_term' : False, 'discount_campaign' : False}}
#        result =  super(sale_order, self).onchange_partner_id(cr, uid, ids, part)['value']
#        campaign = self.pool.get('res.partner').browse(cr, uid, part).discount_campaign.id
#        result['discount_campaign'] = campaign
#        return {'value': result}

#sale_order()
