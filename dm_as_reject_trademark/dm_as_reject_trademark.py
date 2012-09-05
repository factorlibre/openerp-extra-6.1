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

class dm_as_reject(osv.osv):#{{{
    _inherit = "dm.as.reject"
    _columns = {
        'trademark_ids': fields.many2many('dm.trademark','reject_trademark_rel', 'reject_id', 'trademark_id', 'Trademark')
    }
dm_as_reject()#}}}

class dm_trademark(osv.osv):#{{{
    _inherit = "dm.trademark"
    _columns = {
        'reject_id': fields.many2one('dm.as.reject', 'Reject')
    }
dm_trademark()#}}}

class dm_address_segmentation(osv.osv): # {{{
    _name = "dm.address.segmentation"
    _description = "Segmentation"
    _inherit = "dm.address.segmentation"
    
    _columns = {
                
        'trademark_id': fields.many2one('dm.trademark', 'Trademark'),
        }
dm_address_segmentation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
