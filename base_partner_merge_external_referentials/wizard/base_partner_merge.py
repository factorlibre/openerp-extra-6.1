# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA 2011
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

from osv import fields, osv
from tools.translate import _
import tools

class base_partner_merge(osv.osv_memory):
    '''
    Merges two partners
    '''
    _inherit = 'base.partner.merge'

    def check_partners(self, cr, uid, partner_ids, context):
        res = super(base_partner_merge, self).check_partners(cr, uid, partner_ids, context)
        extref_obj = self.pool.get('base.partner.merge.extref')
        if extref_obj.has_an_external_ref(cr, uid, 'res.partner', partner_ids[0], context) and \
           extref_obj.has_an_external_ref(cr, uid, 'res.partner', partner_ids[1], context):
            raise osv.except_osv(_('Error!'), _('You cannot merge 2 partners which both exist on an external referential!'))
        return res

    def custom_updates(self, cr, uid, partner_id, old_partner_ids, context):
        """
        Hook for special updates on old partners and new partner
        Update ir_model_data references to external referentials
        """
        old_partner_ids = old_partner_ids or []
        return self.pool.get('base.partner.merge.extref').\
        update_external_refs(cr, uid, 'res.partner', partner_id, old_partner_ids, context)

base_partner_merge()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

