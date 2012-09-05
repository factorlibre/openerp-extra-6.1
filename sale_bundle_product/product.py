# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_bundle_product for OpenERP                                          #
# Copyright (c) 2011 CamptoCamp. All rights reserved. @author Joel Grand-Guillaume #
# Copyright (c) 2011 Akretion. All rights reserved. @author Sébastien BEAU      #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc


class product_template(osv.osv):
    
    _inherit = "product.template"
    
    _columns = {
        'item_set_ids': fields.many2many('product.item.set', 'product_template_item_set_rel', 'product_template_id', 'product_item_set_id', 'Item sets'),
        'dynamic_price': fields.boolean('Dynamic price computation ?', help="Tic that box to compute the price based on choosen configuration."),
    }


product_template()

