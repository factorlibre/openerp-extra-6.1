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


{
    'name': 'Bundle product (dynamic choice on sale order)',
    'version': '0.1',
    'category': 'Generic Modules/Sales & Purchases',
    'license': 'AGPL-3',
    'description': """This allow you to make a sale order on bundle product, which is a product with dynamical options
    choosen for each SO by the customer.

    Example: 

    Basic PC
      - Cpu 1
      - Ram 4Gb
      - HD 200 Gb""",
    'author': 'Akretion Camptocamp',
    'website': 'http://www.camptocamp.com/ http://www.akretion.com',
    'depends': ['sale'], 
    'init_xml': [],
    'update_xml': [ 
           'wizard/product_configurator_view.xml',
           'sale_bundle_product_view.xml',
           'product_view.xml',
           'sale_view.xml',
           'procurement_view.xml',
           'purchase_view.xml',
      
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

