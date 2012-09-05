# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _name = "account.invoice.line"
    _columns = {
        'discount_description': fields.char('Disc. Name', size=32),
    }

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          address_invoice_id=False, currency_id=False,
                          context=None):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids,
                          product, uom, qty, name, type, partner_id,
                          fposition_id, price_unit, address_invoice_id,
                          currency_id, context=context)

        if not product:
            return res
        pricelist_obj = self.pool.get('product.pricelist')
        partner_obj = self.pool.get('res.partner')
        result = res['value']
        pricelist = False
        if type in ('in_invoice', 'in_refund'):
            if not price_unit and partner_id:
                pricelist = partner_obj.browse(cr, uid, partner_id).\
                        property_product_pricelist_purchase.id
        else:
            if partner_id:
                pricelist = partner_obj.browse(cr, uid, partner_id).\
                        property_product_pricelist.id
        if pricelist:
            pricelists = pricelist_obj.browse(cr, uid, [pricelist])
            if(len(pricelists) > 0 and pricelists[0].visible_discount):
                result['discount_description'] = pricelist_obj.\
                        price_description_get(cr, uid, [pricelist],
                                              product, qty, context)
        return res

account_invoice_line()
