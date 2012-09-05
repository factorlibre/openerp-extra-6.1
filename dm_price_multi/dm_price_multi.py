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

class dm_campaign_proposition_item(osv.osv): # {{{
    _inherit = "dm.campaign.proposition.item"
    _columns = {
       
        'price2': fields.float('Sale Price 2', digits=(16, 2)),
        'price3': fields.float('Sale Price 3', digits=(16, 2)),
        'price4': fields.float('Sale Price 4', digits=(16, 2)),
        'price5': fields.float('Sale Price 5', digits=(16, 2)),
        'price6': fields.float('Sale Price 6', digits=(16, 2)),
        'price7': fields.float('Sale Price 7', digits=(16, 2)),
        'price8': fields.float('Sale Price 8', digits=(16, 2)),
     
    }  
      
dm_campaign_proposition_item() # }}}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
