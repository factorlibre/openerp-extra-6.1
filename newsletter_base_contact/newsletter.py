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

from osv import osv
from osv import fields
from tools.translate import _

class newsletter_newsletter(osv.osv):
    _name = "newsletter.newsletter"
    _description = "Newsletter"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from newsletter_newsletter where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64, required=True),
        'parent_id': fields.many2one('newsletter.newsletter', 'Partner Newsletter', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('newsletter.newsletter', 'parent_id', 'Child Newsletter'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the newsletter without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

newsletter_newsletter()

class newsletter_unsubscribe_reason(osv.osv):
    _name = "newsletter.unsubscribe.reason"
    _description = "Newsletter Unsubscribe reason"

    _columns = {
        'name':fields.char('Name', size=64, required=True),
        'active' : fields.boolean('Active', help="The active field allows you to hide the unsubscribe without removing it."),
    }

    _defaults = {
        'active' : lambda *a: 1,
    }

newsletter_unsubscribe_reason()

class newsletter_subscription(osv.osv):
    _name = "newsletter.subscription"
    _description = "Newsletter subscription"

    _rec_name = 'newsletter_id'

    _columns = {
        'partner_contact_id': fields.many2one('res.partner.contact', 'Contact', select=True, required=True),
        'newsletter_id': fields.many2one('newsletter.newsletter', 'Newsletter', select=True, required=True),
        'newsletter_unsubscribe' : fields.boolean('Unsubscribe' ),
        'newsletter_unsubscribe_reason_id': fields.many2one('newsletter.unsubscribe.reason', 'Newsletter Unsubscribe Reason', select=True),
    }

newsletter_subscription()
