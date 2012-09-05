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

class meeting_confidential_info(osv.osv):

    _name = 'meeting.confidential.info'
    _description = 'Meeting Confidential Info'
    _columns ={
       'name': fields.char('Table',size=32),
       'description':fields.text('Description', required=True),
       'group':fields.selection([('group1','Group1'),('group2','Group2'),('all','Every One')],'Group', required=True)
    }

    def write(self, cr, uid, *args, **args2):
        if 'group' in args[0] and args[0]['group']:
            if args[0]['group'] == "group1":
                args[0]['name'] ="Confidential Info of Group 1"
            else:
                args[0]['name'] ="Confidential Info of Group 2"
        return super(meeting_confidential_info, self).write(cr, uid, *args, **args2)

    def create(self, cr, uid, *args, **args2):
        if 'group' in args[0] and args[0]['group']:
            if args[0]['group'] == "group1":
                args[0]['name'] ="Confidential Info of Group 1"
            else:
                args[0]['name'] ="Confidential Info of Group 2"
        return super(meeting_confidential_info, self).create(cr, uid, *args, **args2)

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.browse(cr, uid, ids, context)
        res = []
        for record in reads:
            res.append((record['id'], record['description']))
        return res

meeting_confidential_info()

class crm_case(osv.osv):

    _inherit = 'crm.case'
    _description = 'crm case'
    _columns = {
       # 'meeting_id' : fields.many2one('meeting.confidential.info','Meeting confidential'),
        'group_id' : fields.many2one('res.groups','Group'),
        'invoice_id' : fields.many2one('account.invoice','Invoice'),
        'event_ids' : fields.many2many('event.event','case_event_rel','case_id','event_id','Events'),
    }

    def default_get(self, cr, uid, fields, context={}):
        data = super(crm_case, self).default_get(cr, uid, fields, context)
        if 'section_id' in context and context['section_id'] :
            data['section_id']=context['section_id']
        if 'partner_id' in context and context['partner_id'] :
            data['partner_id']=context['partner_id']
        return data

crm_case()


class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    _description = 'crm case.section'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        res = super(crm_case_section, self).search(cr, uid, args, offset, limit, order, context, count)
        if context and context.has_key('section_event') and context['section_event']:
            event_sec = []
            event_child_sec = []
            cr.execute('select id from crm_case_section where name=%s',('Events',))
            map(lambda c: event_sec.append(c[0]), cr.fetchall())
            cr.execute('select id from crm_case_section where parent_id in ('+','.join(map(str,event_sec))+')')
            map(lambda c: event_child_sec.append(c[0]), cr.fetchall())
            event_sec.extend(event_child_sec)
            res = [x for x in res if x not in event_sec]
        return res

crm_case_section()

class event_event(osv.osv):
    _inherit = 'event.event'
    _description = 'Event Event'
    _columns = {
        'case_ids' : fields.many2many('crm.case','case_event_rel','event_id','case_id','Cases')
    }
event_event()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

