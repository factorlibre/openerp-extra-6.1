# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields
from osv import osv
from tools.translate import _
import time

partner_address_fields = ('title','firstname','name','street','street2','street3',
                                'street4', 'zip','partner_id.ref','country_id')
order_field = ('title','customer_firstname', 'customer_lastname', 'customer_add1',
                        'customer_add2', 'customer_add3', 'customer_add4', 'zip',
                                                'customer_code', 'country_id')                                

class dm_order(osv.osv): # {{{
    _name = "dm.order"
    _rec_name = 'customer_code'
   
    def calc_prod_amt(self, cr, uid, ids, name, arg, context={}):
        result = {}
        price = 0
        for order in  self.browse(cr, uid, ids):
            for item in order.dm_order_entry_item_ids:
                price += item.price
            result[order.id]=price
        return result
    
    _columns = {
        'raw_datas': fields.char('Raw Datas', size=128),
        'customer_code': fields.char('Customer Code', size=64),
        'title': fields.char('Title', size=32),
        'customer_firstname': fields.char('First Name', size=64),
        'customer_lastname': fields.char('Last Name', size=64),
        'customer_add1': fields.char('Address1', size=64),
        'customer_add2': fields.char('Address2', size=64),
        'customer_add3': fields.char('Address3', size=64),
        'customer_add4': fields.char('Address4', size=64),
        'country_id': fields.many2one('res.country','Country'),
        'zip': fields.char('Zip Code', size=12),
        'zip_summary': fields.char('Zip Summary', size=64),
        'distribution_office': fields.char('Distribution Office', size=64),
        'segment_id': fields.many2one('dm.campaign.proposition.segment',
                                                            'Segment'),
        'offer_step_id': fields.many2one('dm.offer.step','Offer Step'),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done'),
                                    ('error', 'Error')], 'Status', readonly=True),
        'state_msg': fields.text('State Message', readonly=True),
        'dm_order_entry_item_ids':  fields.many2many('dm.campaign.proposition.item',
                                        'dm_order_entry_campaign_proposition_item',
                                        'order_entry_id', 'camp_pro_id',
                                        'Items'), 
        'amount': fields.float('Amount', digits=(16, 2)),
        'prod_amt_total': fields.function(calc_prod_amt,
                                            method=True, type='float',
                                             string='Product Amount Total'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'address_id': fields.many2one('res.partner.address', 'Address'),   
        'sale_order_id' : fields.many2one('sale.order','Sale Order'),     
        'payment_journal_id' : fields.many2one('account.journal','Payment Method'),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def _search_partner_address(self, cr, uid, criteria): 
        partner_address_search = []
        if criteria['title'] :
            address_title = self.pool.get('res.partner.title').search(cr, uid, 
                                        [('name', '=', criteria['title'] ),
                                        ('domain', '=', 'contact')])
            if address_title : 
                title = self.pool.get('res.partner.title').browse(cr, uid, 
                                                        address_title[0]).shortcut
                partner_address_search.append(('title','=',title))
        del(criteria['title'])
        for key,value in criteria.items():
            if value:
                partner_address_search.append((key,'=',value))
        return self.pool.get('res.partner.address').search(cr, uid
                                                ,partner_address_search)                
    def _create_sale_order(self, cr, uid, order_id): 
        order = self.pool.get('dm.order').browse(cr, uid, order_id)
        partner_id =''
        if not order.partner_id and not order.address_id :
            order_field_value = dict(map(lambda o,pa : (pa,getattr(order,o) and \
                    getattr(order,o) or False), order_field,partner_address_fields))
            order_field_value['country_id'] = order_field_value['country_id'].id
            partner_address_id =  self._search_partner_address(cr, uid, order_field_value)
            if partner_address_id :
                partner_id = self.pool.get('res.partner.address').browse(cr, uid,
                                                partner_address_id[0]).partner_id
        elif order.address_id :
            partner_id = order.address_id.partner_id
        elif order.partner_id :
            partner_id = order.partner_id
        if not partner_id :
            return False
            raise osv.except_osv(_('Error !'),
                 _('There is no partner found for this order'))
        address = self.pool.get('res.partner').address_get(cr, uid, [partner_id.id],
                                             ['delivery', 'invoice', 'contact'])
        pricelist_id = order.segment_id and \
                     order.segment_id.proposition_id.customer_pricelist_id and \
                     order.segment_id.proposition_id.customer_pricelist_id.id or \
                     False
        fiscal_position = partner_id.property_account_position and \
                                partner_id.property_account_position.id or False                      
        sale_order_vals = {
            'origin': order.segment_id.code,
            'date_order': time.strftime('%Y-%m-%d'),
            'pricelist_id': pricelist_id,
            'offer_step_id': order.offer_step_id and order.offer_step_id.id or False,
            'partner_id': partner_id.id,
            'partner_order_id': address['contact'],
            'partner_invoice_id': address['invoice'], 
            'partner_shipping_id': address['delivery'], 
            'name': '%s_%s'%(order.segment_id and order.segment_id.code or '',
                                order.customer_code or ''),
            'segment_id': order.segment_id and order.segment_id.id or False,
            'payment_term':partner_id.property_payment_term and \
                                partner_id.property_payment_term.id or False,
            'fiscal_position': fiscal_position,
            'payment_journal_id' : order.payment_journal_id and \
                                order.payment_journal_id.id or False,
            'user_id': partner_id.user_id and partner_id.user_id.id or uid,
        }
        shop_id = self.pool.get('sale.shop').search(cr, uid, [])
        if shop_id: 
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id[0])
            sale_order_vals['shop_id'] = shop.id
            sale_order_vals['project_id'] = shop.project_id.id
        else :
            raise osv.except_osv(_('Error !'),
                 _('There is no shop defined..Please create one shop before confirming order'))
                
        order_lines = []

        for item in order.dm_order_entry_item_ids:
            result = self.pool.get('sale.order.line').product_id_change(cr, uid,
                            [], pricelist_id, item.product_id.id, qty=1,
                            partner_id=partner_id.id,
                            date_order=time.strftime('%Y-%m-%d'),
                            fiscal_position=fiscal_position)
            result['value']['product_id'] = item.product_id.id
            result['value']['product_id'] = item.product_id.id
            order_lines.append([0, 0, result['value']])
        sale_order_vals['order_line'] = order_lines
        return self.pool.get('sale.order').create(cr, uid, sale_order_vals)

    def _create_event(self, cr, uid, so_id):
        so = self.pool.get('sale.order').browse(cr, uid, so_id)
        event_vals = {'action_time': time.strftime('%Y-%m-%d   %H:%M:%S'),
                         'address_id': so.partner_invoice_id.id,
                         'segment_id': so.segment_id.id, 
                         'step_id': so.offer_step_id.id, 
                         'sale_order_id': so_id,
                         'trigger_type_id': 1,}
        self.pool.get('dm.event.sale').create(cr, uid, event_vals)
         
    def create(self, cr, uid, vals, context={}):
        order_id = super(dm_order, self).create(cr, uid, vals, context)
        if 'state' in vals and vals['state']!= 'error' :
            so_id = self._create_sale_order(cr, uid, order_id)
            if so_id :
                self.write(cr, uid, order_id, {'sale_order_id' : so_id})
                self._create_event(cr, uid, so_id)                        
        return order_id

    def onchange_rawdatas(self, cr, uid, ids, raw_datas):
        if not raw_datas:
            return {}
        #raw_datas = "2;US-OERP-0000;JD;Sir;Doe;John;Nowhere Street;;;;US;BN;01652;WORTHING.LU.SX;PI"
        value = raw_datas.split(';')
        key = ['datamatrix_type','segment_id',  'customer_code', 'title', 
               'customer_lastname', 'customer_firstname', 'customer_add1',
               'customer_add2', 'customer_add3', 'customer_add4', 'country_id', 
               'zip_summary', 'zip', 'distribution_office','offer_step_id']
        value = dict(zip(key, value))
        field_check = {'res.country':('country_id','Country'),
                       'dm.campaign.proposition.segment' : ('segment_id','Segment'),
                       'dm.offer.step' : ('offer_step_id','Offer Step'),
            }
        for m in field_check:
            field = field_check[m][0]
            if value.has_key(field) and value[field]:
                f_id = self.pool.get(m).search(cr,uid,[('code','=',value[field])])
                if not f_id:
                    raise osv.except_osv(_('Error !'),
                        _('No %s found for the code '%field_check[m][1]))
                value[field]= f_id[0]
            else:
                raise osv.except_osv(_('Error !'),
                    _('There is no code defined for %s'%field_check[m][1]))
                
        segment_obj =  self.pool.get('dm.campaign.proposition.segment').browse(cr, uid, value['segment_id'])
        pro_items = self.pool.get('dm.campaign.proposition.item').search(cr, uid,
                                                            [('offer_step_id', '=', value['offer_step_id']),
                                                             ('proposition_id', '=', segment_obj.proposition_id.id)])
        value['dm_order_entry_item_ids'] = pro_items
        order_field_value = dict(map(lambda o,pa : (pa,o in value and value[o] \
                                or False), order_field,partner_address_fields))
        partner_address_id = self._search_partner_address(cr, uid, order_field_value)
        if partner_address_id :
            partner_address = self.pool.get('res.partner.address').browse(cr, uid, 
                                                        partner_address_id[0]) 
            value['partner_id'] = partner_address.partner_id.id
            value['address_id'] = partner_address.id
        del(value['datamatrix_type'])
        return {'value': value}
   
dm_order() # }}}

class dm_campaign_proposition_item(osv.osv): #{{{
    _inherit = "dm.campaign.proposition.item"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context == None:
            context = {}
        if 'segment_id' in context and 'offer_step_id' in context and context['segment_id'] and context['offer_step_id']:
            segment_obj =  self.pool.get('dm.campaign.proposition.segment').browse(cr, uid, context['segment_id'])
            pro_items = self.pool.get('dm.campaign.proposition.item').search(cr, uid,
                                                                [('offer_step_id', '=', context['offer_step_id']),
                                                                 ('proposition_id', '=', segment_obj.proposition_id.id)])    
            return pro_items
        return super(dm_campaign_proposition_item, self).search(cr, uid, args, offset, limit, order, context, count)

dm_campaign_proposition_item()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
