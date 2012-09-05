# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import pooler

class res_users(osv.osv):
    _inherit = "res.users"
    _description = 'res.users'

    _columns = {
        'google_email':fields.char('Google Email Id', size=128),
        'google_password': fields.char('Password', size=128),
                }
res_users()

class event_event(osv.osv):
    _inherit = "event.event"
    _description = "Google Event"

    _columns = {
        'google_event_id': fields.char('Google Event Id', size=128, readonly=True),
        'event_modify_date': fields.datetime('Google Modify Date', readonly=True, help='google event modify date'),
        'write_date': fields.datetime('Date Modified', readonly=True, help='tiny event modify date'),
        'create_date': fields.datetime('Date created', readonly=True, help='tiny event create date'),
        'repeat_status': fields.selection([('norepeat', 'Does not Repeat'), ('daily', 'Daily'), ('everyweekday', 'Every weekday(Mon-Fri)'), ('every_m_w_f', 'Every Mon-Wed-Fri'), ('every_t_t', 'Every Tue-Thu'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], 'Repeats', size=32, required=False, readonly=False, help="Repeated status in google"),
        'privacy': fields.selection([('default', 'Default'),('public', 'Public'), ('private', 'Private')], 'Privacy', readonly=True, size=32),
        'email': fields.char('Email', size=256, help="Enter email addresses separated by commas", readonly=True),
        'event':fields.selection([('tiny_event', 'Tiny Event'), ('google_event', 'Google Event')], 'Event Type',required=False, readonly=True,help = "Event of Tiny or Google"),
        'google_event_uri' : fields.char('Google Event URI', size=128, readonly=True),
                }

    _defaults = {
        'repeat_status': lambda *a: 'norepeat',
        'privacy': lambda *a: 'public',
        'event':lambda *a:'tiny_event'
    }

    def unlink(self, cr, uid, ids, context={}):
        event_ids = []
        for event in self.browse(cr, uid, ids, context):
            if event.event == 'tiny_event' or event.event == 'google_event':
                vals = {
                  'google_event_id':event.google_event_id,
                  'google_event_uri':event.google_event_uri
                 }
                res = self.pool.get('google.event').create(cr,uid,vals,context)
                event_ids.append(event.id)
        return super(event_event, self).unlink(cr, uid, event_ids, context)

event_event()

class google_event(osv.osv):
    _name = "google.event"
    _description = "Google Events"

    _columns = {
        'google_event_id': fields.char('Google Event Id', size=128, readonly=True),
        'google_event_uri':fields.char('Google Event URI', size=128, readonly=True)
        }

google_event()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: