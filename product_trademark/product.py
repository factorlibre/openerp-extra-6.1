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

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'manufacturer_pname': fields.char('Manufacturer Name', size=64, help="Manufacturer Product Name"),
        'manufacturer_pref': fields.char('Manufacturer Code', size=64, help="Manufacturer Product Code"),
    }
product_product()

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'manufacturer': fields.many2one('res.partner', 'Manufacturer',
                            domain=[('manufacturer', '=', True)]),
    }
product_template()

class res_partner(osv.osv):
    """ Inherits partner and adds manufacturer boolean """
    _inherit = 'res.partner'

    _columns = {
        'manufacturer': fields.boolean('Manufacturer',
                            help="Check this box if the partner is a manufacturer."),
    }

res_partner()
