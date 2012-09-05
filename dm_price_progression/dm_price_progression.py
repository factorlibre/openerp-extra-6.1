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
from osv import fields
from osv import osv

class dm_campaign_proposition(osv.osv):#{{{
    _inherit = "dm.campaign.proposition"
    _columns = {
        'force_sm_price' : fields.boolean('Force Starting Mail Price'),
        'price_prog_use' : fields.boolean('Price Progression'),
        'sm_price' : fields.float('Starting Mail Price', digits=(16,2)),
#        'prices_prog_id' : fields.many2one('dm.campaign.proposition.prices_progression', 'Prices Progression'),
    }
dm_campaign_proposition()

class dm_campaign_proposition_prices_progression(osv.osv):#{{{
    _name = 'dm.campaign.proposition.prices_progression'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'type': fields.selection([('fixed','Fixed Progression'),('percent','Percentage Progression (%)')], 'Progression Type'),
        'value': fields.float('Value', digits=(16,2)),
    }
dm_campaign_proposition_prices_progression()#}}}

class product_product(osv.osv): # {{{
    _inherit = "product.product"
    
    _columns = {
        'qty_default': fields.float('Default Quantity')
    }
    
product_product() # }}}

class dm_campaign_proposition_item(osv.osv):#{{{
    _inherit = "dm.campaign.proposition.item"

    _columns = {
        'qty_default': fields.float('Default Quantity'),
        'forwarding_charge': fields.float('Forwarding Charge', digits=(16, 2)),
    }
dm_campaign_proposition_item()#}}}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
