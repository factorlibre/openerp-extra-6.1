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


from osv import osv, fields
from tools.translate import _

class dm_customer_partner(osv.osv_memory):

    _name = 'dm.customer.partner'
    _description = 'If customer is not exisit in create partner'

    _columns = {
        'action': fields.selection([('exist', 'Link to an existing partner'), \
                                    ('create', 'Create a new partner')], \
                                    'Action', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner')
        }

    def view_init(self, cr, uid, fields, context=None):
        """
        This function checks for precondition before wizard executes
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values

        """

        order_obj = self.pool.get('dm.order')
        rec_ids = context and context.get('active_ids', [])
        for order in order_obj.browse(cr, uid, rec_ids, context=context):
            if order.partner_id:
                     raise osv.except_osv(_('Warning !'),
                        _('A partner is already defined for this customer.'))

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values

        @return : default values of fields.
        """
        order_obj = self.pool.get('dm.order')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        rec_ids = context and context.get('active_ids', [])
        partner_id = False

        data = context and context.get('active_ids', []) or []
        res = super(dm_customer_partner, self).default_get(cr, uid, fields, context=context)

        for order in order_obj.browse(cr, uid, data, context=context):
            partner_ids = partner_obj.search(cr, uid, [('name', '=', order.customer_firstname)])
            partner_id = partner_ids and partner_ids[0] or False
            if order.address_id  and not partner_id : 
                partner_id = partner_obj.create(cr, uid, {
                    'name': order.customer_firstname,
                    'ref': order.customer_code,
                })
                address_obj.write(cr, uid, order.address_id.id, {
                                           'partner_id' : partner_id})
            if partner_id and not order.address_id :
                address_title = self.pool.get('res.partner.title').search(cr, uid, 
                                            [('name', '=', order.title ),
                                                    ('domain', '=', 'contact')])
                if address_title : 
                    title = self.pool.get('res.partner.title').browse(cr, uid, 
                                                    address_title[0]).shortcut

                address_id = address_obj.create(cr, uid, {
                        'partner_id': partner_id,
                        'firstname': order.customer_firstname,
                        'name': order.customer_lastname,
                        'title': title,
                        'street': order.customer_add1,
                        'street2': order.customer_add2,
                        'street3': order.customer_add3,
                        'street4': order.customer_add4,
                        'zip': order.zip,
                        'country_id': order.country_id and order.country_id.id or False,
                    })
            if 'partner_id' in fields:
                res.update({'partner_id': partner_id})
            if 'action' in fields:
                res.update({'action': partner_id and 'exist' or 'create'})

        return res
    
    def open_create_partner(self, cr, uid, ids, context=None):
        """
        This function Opens form of create partner.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Partner's IDs
        @param context: A standard dictionary for contextual values

        @return : Dictionary value for next form.
        """
        if not context:
            context = {}

        view_obj = self.pool.get('ir.ui.view')
        view_id = view_obj.search(cr, uid, [('model', '=', 'dm.customer.partner'),
                                     ('name', '=', 'dm.customer.partner.view')])
        return {
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id or False,
            'res_model': 'dm.customer.partner',
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            }


    def _create_partner(self, cr, uid, ids, context=None):
        """
        This function Creates partner based on action.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Partner's IDs
        @param context: A standard dictionary for contextual values

        @return : Dictionary {}.
        """
        if not context:
            context = {}

        order_obj = self.pool.get('dm.order')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        partner_ids = []
        partner_id = False
        contact_id = False
        rec_ids = context and context.get('active_ids', [])

        for data in self.browse(cr, uid, ids):
            for order in order_obj.browse(cr, uid, rec_ids):
                if data.action == 'create':
                    partner_id = partner_obj.create(cr, uid, {
                        'name': order.customer_firstname,
                        'ref': order.customer_code,
                    })
                    address_title = self.pool.get('res.partner.title').search(cr,
                                          uid, [('name', '=', order.title ),
                                                ('domain', '=', 'contact')])
                    if address_title : 
                        title = self.pool.get('res.partner.title').browse(cr, uid, 
                            address_title[0]).shortcut


                    address_id = address_obj.create(cr, uid, {
                        'partner_id': partner_id,
                        'firstname': order.customer_firstname,
                        'name': order.customer_lastname,
                        'street': order.customer_add1,
                        'street2': order.customer_add2,
                        'street3': order.customer_add3,
                        'street4': order.customer_add4,
                        'zip': order.zip,
                        'country_id': order.country_id and order.country_id.id or False,
                    })
                else:
                    if data.partner_id:
                        partner_id = data.partner_id.id
                        contact_id = partner_obj.address_get(cr, uid, [partner_id])['default']

                partner_ids.append(partner_id)

                vals = {}
                if partner_id:
                    vals.update({'partner_id': partner_id})
                if contact_id:
                    vals.update({'address_id': contact_id})
                order_obj.write(cr, uid, [order.id], vals)
        return partner_ids

    def make_partner(self, cr, uid, ids, context=None):
        """
        This function Makes partner based on action.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Partner's IDs
        @param context: A standard dictionary for contextual values

        @return : Dictionary value for created Partner form.
        """
        if not context:
            context = {}

        partner_ids = self._create_partner(cr, uid, ids, context)
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'base', 'view_partner_form')
        res = mod_obj.read(cr, uid, result, ['res_id'])

        value = {
            'domain': "[]",
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner',
            'res_id': partner_ids and int(partner_ids[0]) or False,
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'search_view_id': res['res_id']
        }
        return value

dm_customer_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
