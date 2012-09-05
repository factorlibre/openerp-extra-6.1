# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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

from osv import osv

class res_partner(osv.osv):
    """
    Add new values to search Partner:
    ref: =
    name: operator (ilike)
    vat:  operator (ilike)
    phone: = (address)
    email: = (address)
    :return name_get
    """
    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}

        partners = super(res_partner, self).name_search(cr, uid, name, args,
                                                    operator, context, limit)
        ids = [x[0] for x in partners]
        if name and len(ids) == 0:
            partner_ids = self.search(cr, uid, [('vat', operator, name)] + args,
                                      limit=limit, context=context)
            if len(partner_ids) == 0:
                address_ids = self.pool.get('res.partner.address').search(cr,
                                          uid, ['|', '|', ('phone', operator, name),
                                          ('email', operator, name),
                                          ('mobile', operator, name)],
                                          limit=limit, context=context)
                partner_ids = [a.partner_id.id for a in
                               self.pool.get('res.partner.address').browse(cr, uid, address_ids)
                               if a.partner_id]
            ids = [x for x in set(partner_ids)]

        return self.name_get(cr, uid, ids, context)

res_partner()
