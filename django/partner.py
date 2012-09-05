# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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
from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _inherit = "res.partner"

    def dj_check_partner(self, cr, uid, username, email, values, context=None):
        """
        Django Check Partner: check if partner exists with username and email. Create one or update
        username: string
        email: string
        values: dicc
        """
        if context == None:
            context = {}

        ids = self.pool.get('res.partner').search(cr, uid,[('dj_username', '=', username),('dj_email', '=', email)])

        if len(ids) > 0:
            self.pool.get('res.partner').write(cr, uid, ids, values)
            return True
        else:
            if 'name' in values:
                values['dj_username'] = username
                values['dj_email'] = email
                self.pool.get('res.partner').create(cr, uid, values)
                return True
            else:
                return False

    def dj_check_partner_address(self, cr, uid, username, email, values, address_id=None, context=None):
        """
        Django Check Partner Address: check if partner exists with username and email. Check if partner address exists. Create one or update
        username: string
        email: string
        values: dicc
        address_id: integer
        """
        if context == None:
            context = {}

        partner_ids = self.pool.get('res.partner').search(cr, uid,[('dj_username', '=', username),('dj_email', '=', email)])

        if len(partner_ids) > 0:
            partner_id = partner_ids[0]

            if address_id:
                address_ids = self.pool.get('res.partner.address').search(cr, uid,[('id', '=', address_id),('partner_id', '=', partner_id)])
            else:
                address_ids = []

            if len(address_ids) > 0:
                self.pool.get('res.partner.address').write(cr, uid, address_ids, values)
            else:
                values['partner_id'] = partner_id
                if not 'type' in values:
                    values['type'] = 'default'
                self.pool.get('res.partner.address').create(cr, uid, values)
            return True
        else:
            return False

    def dj_check_vat(self, cr, uid, vat, shop_id, context=None):
        """
        Django Check VAT: check if VAT is valid or not
        vat: string (remember need uppercase str)
        """
        if context == None:
            context = {}

        if not shop_id:
            return False

        check_vat = True
        partner_obj = self.pool.get('res.partner')

        vat = vat.upper()
        vat_country = vat[:2]
        vat = vat[2:]
        #TODO: check if vat_country_ids field exist in sale.shop model
        if not hasattr(partner_obj, 'check_vat_' + vat_country.lower()):
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
            for country_id in shop.vat_country_ids:
                vat_country = country_id.code
                if hasattr(partner_obj, 'check_vat_' + vat_country.lower()):
                    check_vat = True
                    break
        
        if check_vat and hasattr(partner_obj, 'check_vat_' + vat_country.lower()):
            check = getattr(partner_obj, 'check_vat_' + vat_country.lower())
            vat_ok = check(vat)
        else:
            vat_ok = False

        return vat_ok

    _columns = {
        'dj_username':fields.char('Username ID', size=100, readonly=True),
        'dj_email':fields.char('Email ID', size=100, readonly=True),
    }

res_partner()
