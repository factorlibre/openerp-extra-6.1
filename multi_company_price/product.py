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

from osv import osv,fields
from tools import config
from tools.translate import _

class product_product(osv.osv):
    _name="product.product"
    _description="Multicompany prices for products"
    _columns={
              'company_standart_price' : fields.property(
                    type='float',
                    string='Company Cost Price',
                    method=True,
                    view_load=True,
                    help='This cost price will be used in a multicompany context. This field is used by the Company Public Pricelist and the Company Default Purchase Pricelist'),
              'company_list_price' : fields.property(
                    type='float',
                    string='Company Sale Price',
                    method=True,
                    view_load=True,
                    help='This Sale price will be used in a multicompany context. This field is used by the Company Public Pricelist and the Company Default Purchase Pricelist'),
              }
product_product()

