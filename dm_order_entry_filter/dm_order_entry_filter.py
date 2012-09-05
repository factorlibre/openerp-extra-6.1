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

class dm_order_session(osv.osv): # {{{
    _inherit = "dm.order.session"
    
    _columns = {
        'country_id': fields.many2one('res.country', 'Country'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'dealer_id': fields.many2one('res.partner', 'Dealer'),
        'trademark_id': fields.many2one('dm.trademark', 'Trademark'),
        'payment_method_id': fields.many2one('dm.payment_method', 'Payment Method'),
    }
    
dm_order_session() # }}}

class dm_order(osv.osv): # {{{
    _inherit= "dm.order"
    
    def _check_filter(self, cr, uid, order_session_id, segment_id, country_id):
        message = ''        
        session_id = self.pool.get('dm.order.session').browse(cr, uid, order_session_id)
        segment_id = self.pool.get('dm.campaign.proposition.segment').browse(cr, uid, segment_id)
        
        field_list = ['trademark_id', 'currency_id', 'dealer_id']
        order_fields = dict(map(lambda x : (x,getattr(segment_id.campaign_id,x).id),field_list))
        order_fields['payment_method_id'] =  segment_id.campaign_id.journal_id.id
        if country_id :
            order_fields['country_id'] = self.pool.get('res.country').browse(cr, uid, country_id).id
        else : 
            order_fields['country_id'] = False
        field_list.extend(['country_id','payment_method_id'])

        filter_fields = dict(map(lambda x : (x,getattr(session_id,x) and \
                            getattr(session_id,x).id or False),field_list))
        message = ''            
        for field in field_list:
            if filter_fields[field] and order_fields[field] != filter_fields[field]:
                msg = "%s does not match with filter value \n" % (field.replace('_id',' name'))
                message = message + msg
        return message
        
    def create(self, cr, uid, vals, context={}):
        so_vals = {}
        if 'order_session_id' in vals and vals['order_session_id'] and \
                 ('state' in vals and vals['state']!= 'error' or True):
            country_id = 'country_id' in vals and vals['country_id'] or False
            message = self._check_filter(cr, uid, vals['order_session_id'],
                                            vals['segment_id'],country_id)
            if message :
                vals.update({'state': 'error', 'state_msg': message})
                return super(dm_order, self).create(cr, uid, vals, context)
            else :
                field_list = ['so_confirm_do','invoice_create_do','invoice_pay_do',
                                                    'invoice_validate_do',]
                session_id = self.pool.get('dm.order.session').browse(cr, uid, 
                                                        vals['order_session_id'])
                if session_id.payment_method_id:
                    so_vals = dict(map(lambda field : (field, \
                                getattr(session_id.payment_method_id,field) and \
                            getattr(session_id.payment_method_id,field) or \
                            False),field_list))
                if session_id.payment_method_id.threshold and 'amount' in vals \
                                    and 'dm_order_entry_item_ids' in vals and \
                                    vals['dm_order_entry_item_ids'] :
                    item_ids = vals['dm_order_entry_item_ids'][0][-1]
                    items = self.pool.get('dm.campaign.proposition.item').browse(
                                                    cr, uid, item_ids, context) 
                    total_price = 0.0
                    for item in items:
                        total_price += item.price
                    expected_amount = total_price * (session_id.payment_method_id.threshold / 100)
                    if vals['amount'] < expected_amount :
                        vals.update({'state':'error',
                        'state_msg':'The amount is lower then defined threshold'})
        order_id = super(dm_order, self).create(cr, uid, vals, context)
        order = self.browse(cr, uid, order_id, context)
        if order.sale_order_id and order.state !='error' and so_vals:
            self.pool.get('sale.order').write(cr, uid, order.sale_order_id.id, so_vals)
        return order_id
        
dm_order() # }}}

class dm_payment_method(osv.osv): # {{{
    _inherit = 'dm.payment_method'
    _columns = {
        'so_confirm_do': fields.boolean('Auto confirm sale order'),
        'invoice_create_do': fields.boolean('Auto create invoice'),
        'invoice_validate_do': fields.boolean('Auto validate invoice'),
        'invoice_pay_do': fields.boolean('Auto pay invoice'),
    }
dm_payment_method() # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
