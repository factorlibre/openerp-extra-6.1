# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
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
from addons.base_vat.base_vat import _ref_vat
import string

class res_partner_contact(osv.osv):
    _name  =  "res.partner.contact"
    _inherit  =  "res.partner.contact"

    _columns  =  {
        'vat': fields.char('VAT', size=32, help="VAT owner account bank."),
    }

    def _split_vat(self, vat):
        vat_country, vat_number = vat[:2].lower(), vat[2:].replace(' ', '')
        return vat_country, vat_number

    def on_change_vat(self, cr, uid, ids, vat, context=None):
        if vat:
            return {'value': {'vat': vat.upper()}}
        return False

    def check_vat(self, cr, uid, ids, context=None):
        '''
        Check the VAT number depending of the country.
        http://sima-pc.com/nif.php
        '''
        partner_obj = self.pool.get('res.partner')
        for contact in self.browse(cr, uid, ids, context=context):
            if not contact.vat:
                return True
            vat_country, vat_number = self._split_vat(contact.vat)
            if hasattr(partner_obj, 'check_vat_' + vat_country.lower()):
                check = getattr(partner_obj, 'check_vat_' + vat_country.lower())
                return check(vat_number)
        return False
            
    def _construct_constraint_msg(self, cr, uid, ids, context=None):
        def default_vat_check(cn, vn):
            # by default, a VAT number is valid if:
            #  it starts with 2 letters
            #  has more than 3 characters
            return cn[0] in string.ascii_lowercase and cn[1] in string.ascii_lowercase
        vat_country, vat_number = self._split_vat(self.browse(cr, uid, ids)[0].vat)
        if default_vat_check(vat_country, vat_number):
            vat_no = vat_country in _ref_vat and _ref_vat[vat_country] or 'Country Code + Vat Number'
            return _('The Vat does not seems to be correct. You should have entered something like this %s'), (vat_no)
        return _('The VAT is invalid, It should begin with the country code'), ()
                
    def _check_duplicate_vat(self, cr, uid, ids, context = None):
        vat = self.browse(cr, uid, ids[0], context = context).vat
        contact_ids = self.search(cr, uid, [('vat', '=', vat), ('vat', '!=', None)], context = context)
        if len(contact_ids) > 1:
            return False
        return True

    _constraints = [
        (check_vat, _construct_constraint_msg, ["vat"]),
        (_check_duplicate_vat, 'Error! You can not create two contacts with the same vat.', ['vat']),
    ]

res_partner_contact()
