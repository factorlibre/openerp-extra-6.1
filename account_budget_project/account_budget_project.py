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

from osv import osv, fields

class crossovered_budget_line(osv.osv):
    _inherit = 'crossovered.budget.lines'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product'),
        'product_qty' : fields.integer('Qty'),
    }

    def on_change_product_id(self, cr, uid, product_id):
        return {'value' : {}}

    def on_change_product_qty(self, cr, uid, product_qty):
        return {'value' : {}}

crossovered_budget_line()

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'

    def _costs_compute(self, cr, uid, ids, name, args, context=None):
        return dict.fromkeys(ids, 0.0)

    def _revenues_compute(self, cr, uid, ids, name, args, context=None):
        return dict.fromkeys(ids, 0.0)

    def _profit_compute(self, cr, uid, ids, name, args, context=None):
        return dict.fromkeys(ids, 0.0)

    def _profit_margin_compute(self, cr, uid, ids, name, args, context=None):
        return dict.fromkeys(ids, 0.0)

    def _profitability_compute(self, cr, uid, ids, name, args, context=None):
        return dict.fromkeys(ids, 0.0)

    _columns = {
        'costs' : fields.function(_costs_compute, string='Costs', method=True, store=True,
                                  type='float'),
        'revenues' : fields.function(_revenues_compute, string='Revenues', method=True, store=True,
                                     type='float'),
        'profit' : fields.function(_profit_compute, string='Profit', method=True, store=True,
                                   type='float'),
        'profit_margin' : fields.function(_profit_margin_compute, string='Profit Margin', method=True,
                                          store=True, type='float'),
        'profitability' : fields.function(_profitability_compute, string='Profitability',
                                          method=True, store=True, type='float'),
    }

account_analytic_account()
