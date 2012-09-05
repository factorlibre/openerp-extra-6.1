#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
import time
from osv import osv
from osv import fields
from datetime import datetime

class reminder_reminder(osv.osv):
    '''
    Reminder
    '''
    _name = 'reminder.reminder'
    _description = 'Reminder'
    
    _columns = {
        'name':fields.char('Name', size=256, required=True, readonly=False),
        'model_id':fields.many2one('ir.model', 'Model', required=True),
        'field_id':fields.many2one('ir.model.fields', 'Field Name', required=False),
        'domain':fields.char('Domain', size=1024, required=False, readonly=False),
        'start_date': fields.datetime('Start Date', required=True),
        'end_date': fields.date('End Date'),
        'action_id':fields.many2one('ir.actions.server', 'Action', required=True),
        'note': fields.text('Description'),
        'match':fields.selection([
            ('one','Any One'),
            ('all','All'),
            ('true','Always True')
        ],'Match', select=True, readonly=False, required=True),
        'line_ids':fields.one2many('reminder.reminder.line', 'reminder_id', 'Conditions', required=False),
        'state':fields.selection([
            ('draft','Stop'),
            ('done','Running'),
        ],'State', select=True, readonly=True),
        'running':fields.selection([
            ('hour','Hourly'),
            ('day','Daily'),
            ('month','Monthly'),
        ],'Execute Mode', select=True, readonly=False),
    }
    _defaults = {
        'domain': lambda *a: "[]",
        'state': lambda *a: "draft",
        'running': lambda *a: "hour",
    }
    
    def start(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'done'})
        return True
    
    def stop(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
        
    def _call(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to process cases for date actions
        Only works on not done and cancelled cases
        '''
        action_pool = model_pool = self.pool.get('ir.actions.server')
        if not ids:
            ids = self.search(cr, uid, [('state','=','done')])

        for rem in self.browse(cr, uid, ids):
            model_pool = self.pool.get(rem.model_id.model)
            domain = eval(rem.domain, {})
            mids = model_pool.search(cr, uid, domain)

            res = []
            for rs in model_pool.browse(cr, uid, mids):
                data = {
                    'object':rs,
                    'context':context,
                    'time':time,
                    'datetime':datetime
                }
                final_result = True
                any_true = False
                for cond in rem.line_ids:
                    result = eval(cond.name, data)
                    final_result = final_result and result
                    if result:
                        any_true = result

                result = None

                if rem.match == 'all' and final_result:
                    result = action_pool.run(cr, uid, [rem.action_id.id], {'active_id':rs.id, 'active_ids':[rs.id]})
                elif rem.match == 'one' and any_true:
                    result = action_pool.run(cr, uid, [rem.action_id.id], {'active_id':rs.id, 'active_ids':[rs.id]})
                elif rem.match == 'true':
                    result = action_pool.run(cr, uid, [rem.action_id.id], {'active_id':rs.id, 'active_ids':[rs.id]})
                    
                log = {
                    'name':'Called server actions %s' % (rem.action_id.name),
                    'date':time.strftime('%Y-%m-%d'),
                    'reminder_id':rem.id
                }
                if result == None or type(result) == type({}):
                    log['state'] = 'warning'
                    log['note'] = 'Client Action can not be work with Reminder'
                elif result == False:
                    log['state'] = 'exception'
                else:
                    log['state'] = 'info'
                self.pool.get('reminder.log').create(cr, uid, log)
        return True
    
reminder_reminder()

class reminder_reminder_line(osv.osv):
    '''
    Reminder Conditions
    '''
    _name = 'reminder.reminder.line'
    _description = 'Reminder Conditions'
    
    _columns = {
        'reminder_id':fields.many2one('reminder.reminder', 'Model', required=False),
        'name':fields.char('Condition', size=256, required=True, readonly=False),
        'sequence': fields.integer('Sequence'),
    }
reminder_reminder_line()

class user_reminder(osv.osv):
    '''
    User Reminders
    '''
    _name = 'res.reminder'
    _description = 'User Reminders'
    _columns = {
        'user_id':fields.many2one('res.users', 'User', required=False, readonly=True),
        'name':fields.char('Name', size=1024, required=True, readonly=False),
        'note': fields.text('Description'),
        'datetime': fields.date('Date of Event', required=True),
        'start_date': fields.date('Start Date', required=True),
        'active':fields.boolean('Active', required=False),
        'repeat':fields.boolean('Repeat ?', required=False),
        'state':fields.selection([
            ('day','Daily'),
            ('month','Monthly'),
            ('year','Yearly'),
        ],'Repeat Every', select=True, readonly=False),
        'notify':fields.selection([
            ('email','Email Address'),
            ('mobile','Mobile Number'),
        ],'Notify On', select=True, reduired=True),
        'email':fields.char('Email / Mobile', size=1024, help="This can be any things, it can be email address or mobile according to usage of action"),
    }
    _defaults = {
        'datetime': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        'active': lambda *a: True,
        'state': lambda *a: 'year',
        'notify': lambda *a: 'email',
        'user_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).id,
    }
    
    def onchange_userid(self, cr, uid, ids, userid, notify, context=None):
        notify_on = False
        if userid:
            user_add = self.pool.get('res.users').browse(cr, uid, userid, context=context).address_id
            if notify == 'email':
                notify_on = user_add.email
            elif notify == 'mobile':
                notify_on = user_add.mobile        

        return {
            'value': {'email': notify_on}
        }
    
user_reminder()

class reminder_reminder_log(osv.osv):
    '''
    Reminder Log
    '''
    _name = 'reminder.log'
    _description = 'Reminder Log'
    _columns = {
        'reminder_id':fields.many2one('reminder.reminder', 'Reminder', readonly=True, select=True),
        'name':fields.char('Log Entry', size=1024, readonly=True, select=True),
        'date': fields.datetime('Date', readonly=True, select=True),
        'note': fields.text('Description', readonly=True, select=True),
        'state':fields.selection([
            ('info','INFO'),
            ('exception','ERROR'),
            ('warning','WARNING'),
        ],'Level', readonly=True, select=True),
    }
reminder_reminder_log()
