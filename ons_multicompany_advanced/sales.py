# -*- coding: utf-8 -*-
#
#  File: sales.py
#  Module: ons_multicompany_advanced
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc
from osv import osv, fields, orm

class purchase_order(osv.osv):
	_inherit = 'purchase.order'
	def wkf_approve_order(self, cr, uid, ids):
		res = super(purchase_order,self).wkf_approve_order(cr, uid, ids)
		products_obj = self.pool.get('product.product')
		sale_obj = self.pool.get('sale.order')
		sale_line_obj = self.pool.get('sale.order.line')
		partner_obj = self.pool.get('res.partner')
		companies_obj = self.pool.get('res.company')

		for po in self.browse(cr, uid, ids):
			seller_user = po.partner_id.user_id
			seller_user_id = False
			if not seller_user or seller_user is None:
				users = self.pool.get('res.users')
				for usr_id in users.search(cr, uid, []):
					usr = users.browse(cr, uid, usr_id)
					if usr.company_id.partner_id.id == po.partner_id.id:
						seller_user = usr
						break
			if seller_user:
				seller_user_id = seller_user.id
			if not seller_user_id:
				continue
			
			# Here, the supplier becomes the seller, the destinee of the supply becomes the buyer
			seller_company_id = False
			seller_shops = []
			for comp in companies_obj.browse(cr, uid, companies_obj.search(cr, uid, [])):
				if po.partner_id.id == comp.partner_id.id:
					seller_company_id = comp.id
					break
			if seller_company_id:
				seller_shops = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',seller_company_id)])
			if not seller_shops or len(seller_shops) < 1:
				raise orm.except_orm("Problem", "The company '%s' should have a shop for its sales" %po.partner_id.name )
			seller_shop_id = seller_shops[0]
			selling_company = po.company_id

			buying_partner = selling_company.partner_id
			buying_part_id = buying_partner.id
			buying_partner_addr = partner_obj.address_get(cr, uid, [buying_part_id], ['invoice', 'delivery', 'contact'])
			default_pricelist = partner_obj.browse(cr, uid, buying_part_id, {}).property_product_pricelist.id
			fpos = partner_obj.browse(cr, uid, buying_part_id, {}).property_account_position
			fpos_id = fpos and fpos.id or False

			vals = {
				'origin': '%s/%s' % (str(po.name),str(po.origin)),
				'picking_policy': 'direct',
				'shop_id': seller_shop_id,
				'partner_id': buying_part_id,
				'pricelist_id': default_pricelist,
				'partner_invoice_id': buying_partner_addr['invoice'],
				'partner_order_id': buying_partner_addr['contact'],
				'partner_shipping_id': buying_partner_addr['delivery'],
				'order_policy': 'manual',
				'date_order': time.strftime('%Y-%m-%d'),
				'order_policy': po.invoice_method=='picking' and 'picking' or 'manual',
				'fiscal_position': fpos_id
			}
			new_id = sale_obj.create(cr, seller_user_id, vals)
			
			fpos = buying_partner.property_account_position and buying_partner.property_account_position.id or False
			for line in po.order_line:
				prod = line.product_id
				value = sale_line_obj.product_id_change(cr, uid, [], default_pricelist,
						prod.id, qty=line.product_qty, partner_id=buying_part_id, fiscal_position=fpos)['value']
				value.update({'partner_id':buying_part_id, 'prod_categ_id':prod.categ_id.id})
				value['price_unit'] = line.price_unit
				value['product_id'] = line.product_id.id
				value['product_uos'] = value.get('product_uos', False)
				value['product_uom_qty'] = line.product_qty
				value['order_id'] = new_id
				tmp = products_obj.get_contextual_values(cr, seller_user_id, [prod.id], 'procure_method', False)
				value['type'] = tmp[prod.id]
				sale_line_obj.create(cr, seller_user_id, value)

		return res
purchase_order()
