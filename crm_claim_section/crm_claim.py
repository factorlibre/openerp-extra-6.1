# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class crm_claim(osv.osv):
    _inherit = "crm.claim"
    
    def message_new(self, cr, uid, msg, context=None):
        """
        Add new section when new email message arrives

        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks
        """

        res = super(crm_claim, self).message_new(cr, uid, msg, context)

        to = msg.get('to')
        sections = self.pool.get('crm.case.section').search(cr, uid, [('reply_to','=',to)])

        if len(sections) > 0:
            vals = {'section_id': sections[0]}
            self.write(cr, uid, [res], vals, context)

        return res

crm_claim()

