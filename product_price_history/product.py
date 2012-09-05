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

import time

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'product_history': fields.one2many('product.price.history', 'product_id', 'Price History', readonly=True),
    }

    def write(self, cr, uid, ids, values, context=None):
        """
        Add old Sale Price or Sale Cost to historial
        """
        for id in ids:
            prod_template = self.browse(cr, uid, id)

            history_values = {}
            if 'list_price' in values or 'standard_price' in values:
                history_values['list_price'] = prod_template.list_price
                history_values['standard_price'] = prod_template.standard_price
                history_values['product_id'] =  prod_template.id
                history_values['date_to'] =  time.strftime('%Y-%m-%d %H:%M:%S')

                self.pool.get('product.price.history').create(cr, uid, history_values)

        return super(product_template, self).write(cr, uid, ids, values, context=context)

product_template()
