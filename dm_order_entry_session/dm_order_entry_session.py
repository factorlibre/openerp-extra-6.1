# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import fields
from osv import osv
import time
from time import strftime

from tools.translate import _

STATE = [ #{{{
     ('pending','Pending'),
     ('running','Running'),
     ('done','Done')
] # }}}

class dm_order_session(osv.osv): # {{{
    _name = "dm.order.session"
    _rec_name = "user_id"
    
    _columns = {
        'user_id': fields.many2one('res.users', 'User', readonly=True ),
        'date_start': fields.datetime('Start Date'),
        'date_stop': fields.datetime('Stop Date'),
        'order_ids': fields.one2many('dm.order', 'order_session_id', 'Order'),
        'state': fields.selection(STATE, 'Status', size=32),

    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        
        'state': lambda *a: 'pending',
    }
    
    def start_session(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'running'})
        return True
    
    def stop_session(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'done',
                                  'date_stop': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
dm_order_session() # }}}

class dm_order(osv.osv): # {{{
    _inherit= "dm.order"
    
    _columns = {
        'order_session_id': fields.many2one('dm.order.session', 'Session')  
    }
    
    def create(self, cr, uid, vals, context={}):
        if vals.has_key('order_session_id') and vals['order_session_id']:
            session_obj = self.pool.get('dm.order.session').browse(cr, uid, vals['order_session_id'])
            if not session_obj.state == 'running':
                raise osv.except_osv(_('Error!'),_("There is no running session for this order entry"))
        return super(dm_order, self).create(cr, uid, vals, context)
    
dm_order() # }}}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: