# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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

from osv import fields, osv
from tools.translate import _

import decimal_precision as dp
import time

class product_price_history(osv.osv):
    _name = 'product.price.history'
    _rec_name = 'product_id'
    _order = 'date_to desc'

    _columns = {
        'date_to': fields.datetime('Date To', readonly=True, required=True),
        'product_id':  fields.many2one('product.template', 'Product', readonly=True, required=True),
        'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Sale Price'), readonly=True),
        'standard_price': fields.float('Cost Price', digits_compute=dp.get_precision('Account'), readonly=True),
    }

product_price_history()
