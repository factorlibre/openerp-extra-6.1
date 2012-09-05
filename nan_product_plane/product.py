# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2011  NaN Projectes de Programari Lliure S.L.
#                   (http://www.nan-tic.com) All Rights Reserved.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv

class nan_product_plane(osv.osv):
    _name = 'product.plane'

    def _get_company_user(self,cr,uid,context=None):
        if context == None:
            context = {}
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64),
        'image': fields.binary('Image'),
        'company_id': fields.many2one ( 'res.company', 'Company', required=True ), 
    }

    _defaults = {
            'company_id': _get_company_user, 
    }
nan_product_plane()

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'plane_id': fields.many2one ( 'product.plane', 'Plane' )
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
