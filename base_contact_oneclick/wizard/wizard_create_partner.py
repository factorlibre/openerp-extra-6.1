# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields,osv
from tools.translate import _

class create_partner_wizard(osv.osv_memory):
    _name = 'base.contact.create.partner.wizard'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'customer': fields.boolean('Customer', help="Check this box if the partner is a customer."),
        'supplier': fields.boolean('Supplier', help="Check this box if the partner is a supplier. If it's not checked, purchase people will not see it when encoding a purchase order."),       
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'Fed. State', domain="[('country_id','=',country_id)]"),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('E-Mail', size=240),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
        'message': fields.text('Message'),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
        'customer': True,
    }

    def res_partner_values(self, form):
        values = {}
        values['name'] = form.name
        if 'customer' in form: values['customer'] = form.customer
        if 'supplier' in form: values['supplier'] = form.supplier
        return values

    def res_partner_address_values(self, form, partner_id):
        values = {}
        values['name'] = form.name
        values['partner_id'] = partner_id
        if 'street' in form: values['street'] = form.street
        if 'street2' in form: values['street2'] = form.street2
        if 'zip' in form: values['zip'] = form.zip
        if 'city' in form: values['city'] = form.city
        if 'state_id' in form: values['state_id'] = form.state_id.id
        if 'country_id' in form: values['country_id'] = form.country_id.id
        if 'email' in form: values['email'] = form.email
        if 'phone' in form: values['phone'] = form.phone
        if 'fax' in form: values['fax'] = form.fax
        if 'mobile' in form: values['mobile'] = form.mobile
        return values
        
    def res_partner_contact_values(self, form):
        values = {}
        # split name: first_name + name
        name = form.name.split(' ')
        if len(name) > 1:
            values['first_name'] = name[0]
            del name[0]
            values['name'] = " ".join(name)
        else:
            values['first_name'] = ''
            values['name'] = form.name
        if 'mobile' in form: values['mobile'] = form.mobile
        if 'country_id' in form: values['country_id'] = form.country_id.id
        if 'email' in form: values['email'] = form.email
        return values

    def res_partner_job_values(self, form, partner_address_id, partner_contact_id):
        values = {}
        values['address_id'] = partner_address_id
        values['contact_id'] = partner_contact_id
        if 'email' in form: values['email'] = form.email
        if 'phone' in form: values['phone'] = form.phone
        if 'fax' in form: values['fax'] = form.fax
        return values

    def create_partner(self, cr, uid, ids, data, context={}):
        """
        Create a new partner, address, contact and job from wizard. On click for crete this relation models
        """
        form = self.browse(cr, uid, ids[0])

        partner_ids = self.pool.get('res.partner').search(cr, uid, [('name','=',form.name)])
        if len(partner_ids) > 0:
            raise osv.except_osv(_("Alert"), _("This partner exists."))
        else:
            #create partner
            values = self.res_partner_values(form)
            partner_id = self.pool.get('res.partner').create(cr, uid, values)

            #create address
            values = self.res_partner_address_values(form, partner_id)
            partner_address_id = self.pool.get('res.partner.address').create(cr, uid, values)

            #create contact
            values = self.res_partner_contact_values(form)
            #check if this contact exists... maybe
            partner_contact_ids = self.pool.get('res.partner.contact').search(cr, uid, [('first_name','=',values['first_name']),('name','=',values['name'])])
            
            if len(partner_contact_ids) > 0:
                partner_contact_id = partner_contact_ids[0]
            else:
                partner_contact_id = self.pool.get('res.partner.contact').create(cr, uid, values)

            #create job
            values = self.res_partner_job_values(form, partner_address_id, partner_contact_id)
            partner_job_id = self.pool.get('res.partner.job').create(cr, uid, values)
            
            #out wizard
            values = {
                'message':_('Partner %s created with ID %s, Address ID %s and Contact ID %s') % (form.name, partner_id, partner_address_id, partner_contact_id),
                'state':'done',
            }
            self.write(cr, uid, ids, values)
            return partner_id, partner_address_id, partner_contact_id, partner_job_id

create_partner_wizard()
