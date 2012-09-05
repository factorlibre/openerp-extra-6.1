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

class dm_payment_rule(osv.osv): # {{{
    _name = 'dm.payment_rule'
    _columns = {
                
        'name': fields.char('Name', size=64, required=True),
        'dealer_id': fields.many2one('res.partner','Dealer', domain="[('category_id.name','=','Dealer')]"),
        'trademark_id': fields.many2one('dm.trademark', 'Trademark'),
        'country_id': fields.many2one('res.country', 'Country'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'payment_method_id': fields.many2one('dm.payment_method', 'Payment Method'),
        'journal_id': fields.many2one('account.journal', 'Journal'),

    }
dm_payment_rule() # }}}

class dm_campaign_payment_rule(osv.osv): # {{{
    _name = 'dm.campaign.payment_rule'
    _columns = {
      
        'name': fields.char('Name', size=64, required=True),
        'dealer_id': fields.many2one('res.partner','Dealer', domain="[('category_id.name','=','Dealer')]"),
        'trademark_id': fields.many2one('dm.trademark', 'Trademark'),
        'country_id': fields.many2one('res.country', 'Country'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'payment_method_id': fields.many2one('dm.payment_method', 'Payment Method'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),

    }
dm_campaign_payment_rule() # }}}

class dm_campaign(osv.osv): # {{{
    _inherit = "dm.campaign"
    _columns = {
                
        'payment_rule_ids': fields.one2many('dm.campaign.payment_rule', 'campaign_id',
                                            'Payment Rules'), 
    }    
dm_campaign() # }}}

class dm_campaign_proposition_payment_rule(osv.osv): # {{{
    _name = 'dm.campaign.proposition.payment_rule'
    _columns = {
      
        'name': fields.char('Name', size=64, required=True),
        'dealer_id': fields.many2one('res.partner','Dealer', domain="[('category_id.name','=','Dealer')]"),
        'trademark_id': fields.many2one('dm.trademark', 'Trademark'),
        'country_id': fields.many2one('res.country', 'Country'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'payment_method_id': fields.many2one('dm.payment_method', 'Payment Method'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'proposition_id': fields.many2one('dm.campaign.proposition', 'Campaign Proposition'),

    }
dm_campaign_proposition_payment_rule() # }}}

class dm_campaign_proposition(osv.osv): # {{{
    _inherit = "dm.campaign.proposition"
    _columns = {
                
        'payment_rule_ids': fields.one2many('dm.campaign.proposition.payment_rule', 'proposition_id',
                                            'Payment Rules'), 
    }  
      
dm_campaign_proposition() # }}}
class dm_order(osv.osv): # {{{
    _inherit= "dm.order"
    
    def create(self, cr, uid, vals, context={}):
        if 'order_session_id' in vals and vals['order_session_id']:
            country_id = 'country_id' in vals and vals['country_id'] or False
            message = self._check_filter(cr, uid, vals['order_session_id'],
                                            vals['segment_id'],country_id)
            if message :
               vals['state'] = 'error'
               return super(dm_order, self).create(cr, uid, vals, context)
            session_id = self.pool.get('dm.order.session').browse(cr, uid, vals['order_session_id'])
            field_list = ['trademark_id', 'currency_id', 'dealer_id', 
                                                'country_id','payment_method_id']
            payment_rule_search = []                                                
            for field in field_list :
                if getattr(session_id,field) :
                    payment_rule_search.append((field, '=', getattr(session_id,field).id))
            payment_rule_obj = self.pool.get('dm.payment_rule')
            payment_rule_id =  payment_rule_obj.search(cr, uid, payment_rule_search)         
            if payment_rule_id :
                payment_rule = payment_rule_obj.browse(cr, uid, payment_rule_id[0])
                vals['payment_journal_id'] = payment_rule.journal_id.id
            else :
                vals['state'] = 'error'
                vals['state_msg'] = 'There is no Payment Rule defined that matches that session,Thus can not create the sale order'
        return super(dm_order, self).create(cr, uid, vals, context)
dm_order() # }}}               

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
