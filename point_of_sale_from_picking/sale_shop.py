# -*- coding: utf-8 -*-
##############################################################################
#
#    point_of_sale_from_picking module for OpenERP, profile for 2ed customer
#
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com)
#       All Rights Reserved, Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (c) 2009 SYLEAM (http://syleam.fr)
#       All Rights Reserved, Christophe Chauvet <christophe.chauvet@syleam.fr>
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#       All Rights Reserved, Jesús Martín <jmartin@zikzakmedia.com>
#
#    This file is a part of point_of_sale_extension
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields

class sale_shop(osv.osv):
    _inherit = 'sale.shop'
    _columns = {
        'pos_warn_sale_order': fields.boolean('Product in sale order warning',
            help="Shows a warning if a product added in the POS order has already been requested by the partner (the partner has a sale order with this product), so the user can decide if is better to do a POS order from a sale order."),
    }
    _defaults = {
        'pos_warn_sale_order': lambda *a: True,
    }

sale_shop()
