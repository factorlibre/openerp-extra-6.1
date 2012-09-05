# -*- coding: utf-8 -*-
##############################################################################
#
#    account_fiscal_position_name module for OpenERP, Show name instead of description
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>) 
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of account_fiscal_position_name
#
#    account_fiscal_position_name is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_fiscal_position_name is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv

class account_tax(osv.osv):
    _inherit = 'account.tax'

    def name_get(self, cr, uid, ids, context=None):
        """ Get name of account_tax"""
        if not context:
            context = {}
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['description','name'], context):
            name = record['name'] or record['description']
            res.append((record['id'],name ))
        return res

account_tax()

class account_tax_template(osv.osv):
    _inherit = 'account.tax.template'

    def name_get(self, cr, uid, ids, context=None):
        """ Get name of account_tax_template"""
        if not context:
            context = {}
        if not len(ids):
            return []
        res = []
        for record in self.read(cr, uid, ids, ['description','name'], context):
            name = record['name'] or record['description']
            res.append((record['id'],name ))
        return res

account_tax_template()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
