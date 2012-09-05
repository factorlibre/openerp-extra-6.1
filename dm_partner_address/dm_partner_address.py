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

class dm_matchcode(osv.osv):
    _name = 'dm.matchcode'
    _description = 'Matchcodes for DM'
    
    _columns = {
            'name': fields.char('Name', size=64, required=True),
            'matchexp': fields.char('Match Expression', size=128, help="""This string defines \
                     the matchcode expression used to compute the matchcode of a \
                     customer (partner address). The expression must be a pair of \
                     key:value separated by a coma. Example : firstname:7, lastname:1, \
                     street1:-3, city:4, zip:3. A minus sign means that x last characters of the string"""),
            'country_id': fields.many2one('res.country', 'Country')
        }
        
dm_matchcode()

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'firstname': fields.char('First Name', size=64),
        'name_complement': fields.char('Name Complement', size=64),
        'street3': fields.char('Street3', size=128),
        'street4': fields.char('Street4', size=128),
        'moved': fields.boolean('Moved'),
        'quotation': fields.float('Quotation', digits=(16,2)),
        'origin_partner': fields.char('Origin Partner', size=64),
        'origin_support': fields.char('Origin Support', size=64),
        'origin_keyword': fields.char('Origin Keyword', size=64), 
        'origin_campaign_id': fields.many2one('dm.campaign', 'Origin Campaign'),
        'origin_country_id': fields.many2one('res.country', 'Origin Country'),
        'date_birth': fields.datetime('Date of Birth'),
        'matchcode_id': fields.many2one('dm.matchcode', 'Matchcode')
    }
res_partner_address()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
