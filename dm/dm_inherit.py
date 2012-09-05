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

class res_country(osv.osv):#{{{
    _inherit = 'res.country'
    _columns = {
        'main_language': fields.many2one('res.lang', 'Main Language',
                                          ondelete = 'cascade',),
        'main_currency': fields.many2one('res.currency', 'Main Currency', 
                                                 ondelete = 'cascade'),
        'forwarding_charge': fields.float('Forwarding Charge', digits=(16, 2)),
        'journal_id': fields.many2many('account.journal', 
                                    'country_payment_method_rel', 'country_id',
                                    'journal_id', 'Payment Methods', 
                                     domain=[('type', '=', 'cash')]),
    }
res_country()#}}}

class res_partner_address(osv.osv) : #{{{
    _inherit = 'res.partner.address'
    _columns = {
        'decoy_address' : fields.boolean('Decoy Address', help='A decoy address is an address used to identify unleagal uses of a customers file'),
        'decoy_owner' : fields.many2one('res.partner','Decoy Address Owner', help='The partner this decoy address belongs to'),
        'decoy_external_ref' : fields.char('External Reference', size=64, help='The reference of the decoy address for the owner'),
        'decoy_media_ids': fields.many2many('dm.media','dm_decoy_media_rel','decoy_media_id','customer_id','decoy address for Media'),
    }
res_partner_address() #}}}

class res_partner(osv.osv):#{{{
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'country_ids': fields.many2many('res.country', 'partner_country_rel',
                                        'partner_id', 'country_id',
                                        'Allowed Countries'),
        'state_ids': fields.many2many('res.country.state', 'partner_state_rel',
                                      'partner_id', 'state_id',
                                     'Allowed States'),
        'language_ids': fields.many2many('res.lang', 'dm_customer_langs', 
                                         'lang_id', 'customer_id',
                                        'Other Languages'),
        'prospect_media_ids': fields.many2many('dm.media',
                                               'dm_customer_prospect_media',
                                               'prospect_media_id',
                                               'customer_id',
                                               'Prospect for Media'),
        'client_media_ids': fields.many2many('dm.media',
                                             'dm_customer_client_media',
                                             'client_media_id',
                                             'customer_id',
                                             'Client for Media'),
        'decoy_address': fields.boolean('Decoy Address', 
                        help='A decoy address is an address used to identify unleagal uses of a customers file'),
        'decoy_owner': fields.many2one('res.partner', 'Decoy Address Owner',
                            help='The partner this decoy address belongs to'),
        'decoy_external_ref': fields.char('External Reference', size=64, 
                        help='The reference of the decoy address for the owner'),
        'decoy_media_ids': fields.many2many('dm.media', 'dm_decoy_media_rel', 
                                            'decoy_media_id',
                                            'customer_id',
                                            'decoy address for Media'),
        'decoy_for_campaign': fields.boolean('Used for Campaigns',
                                help='Define if this decoy address can be used with campaigns'),
        'decoy_for_renting': fields.boolean('Used for File Renting', 
                              help='Define if this decoy address can be used with used with customers files renting'),

    }
    def _default_category(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            return [context['category_id']]
        elif 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr, uid,
                                    [('name', 'ilike', context['category'])])[0]
            return [id_cat]
        return []

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        def id_get(cr, model, id_str, mod):
            if '.' in id_str:
                mod, id_str = id_str.split('.')
            try:
                idn = self.pool.get('ir.model.data')._get_id(cr, uid, mod, id_str)
                res = int(self.pool.get('ir.model.data').read(cr, uid, [idn], ['res_id'])[0]['res_id'])
            except Exception, e:
                res = None
            return res
        # END def id_get.

        if  context is None:
            context = {}

        if 'category_xml_id' in context and context['category_xml_id']:
            cat_id = id_get(cr, 'res.partner.category', context['category_xml_id'], 'dm')

            if cat_id is not None:
                if args:
                    old_args = args
                    args = []
                    for arg in old_args:
                        if arg[0] == 'category_id':
                            arg = ['category_id', 'in', [cat_id]]
                        args.append(arg)
                else:
                    args = [('category_id', 'in', [cat_id])]

        res = super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        return res

#    def _default_all_country(self, cr, uid, context={}):
#        id_country = self.pool.get('res.country').search(cr,uid,[])
#        return id_country

#    def _default_all_state(self, cr, uid, context={}):
#        id_state = self.pool.get('res.country.state').search(cr,uid,[])
#        return id_state

    _defaults = {
        'category_id': _default_category,
#        'country_ids': _default_all_country,
#        'state_ids': _default_all_state,
    }
res_partner()#}}}

"""
class sale_order(osv.osv):#{{{
    _name = "sale.order"
    _inherit="sale.order"
    _columns = {
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'segment_id': fields.many2one('dm.campaign.proposition.segment',
                                                                     'Segment'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'lines_number': fields.integer('Number of sale order lines'),
        'so_confirm_do': fields.boolean('Auto confirm sale order'),
        'invoice_create_do': fields.boolean('Auto create invoice'),
        'invoice_validate_do': fields.boolean('Auto validate invoice'),
        'invoice_pay_do': fields.boolean('Auto pay invoice'),
    }
    
sale_order()#}}}
"""


class product_product(osv.osv): # {{{
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'country_ids': fields.many2many('res.country', 'product_country_rel',
                                'product_id', 'country_id','Forbidden Countries'),
        'state_ids': fields.many2many('res.country.state', 'product_state_rel',
                                    'product_id', 'state_id', 'Forbidden States'),
        'language_id': fields.many2one('res.lang', 'Language'),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
                                                    context={}, count=False):
            result = super(product_product,self).search(cr, uid, args, offset, 
                                                 limit, order, context, count)
            if 'offer_id' in context and context['offer_id']:
                result = []
                offer_browse_id = self.pool.get('dm.offer').browse(cr, uid, 
                                                            context['offer_id'])
                for step in offer_browse_id.step_ids:
                    for item in step.item_ids:
                        result.append(item.id)
            return result
product_product() # }}}

class actions_server(osv.osv): # {{{
    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'
    _columns = {
        'dm_action': fields.boolean('Action')
    }
actions_server() # }}}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
