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


class dm_workitem(osv.osv): # {{{
    _inherit = "dm.workitem"
    SELECTION_LIST = [
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('cancel', 'Cancelled'),
        ('freeze', 'Frozen'),
        ('done', 'Done')
    ] # }}}

    _columns = {
        'tr_from_id': fields.many2one('dm.offer.step.transition', 'Source Transition', ondelete="set null"),
        'state': fields.selection(SELECTION_LIST, 'Status', select="1"),
    }

dm_workitem() # }}}


SYSMSG_STATES = [ # {{{
    ('draft', 'Draft'),
    ('open', 'Open'),
    ('close', 'Close'),
    ('pending', 'Pending'),
    ('cancel', 'Cancelled'),
    ('freeze', 'Frozen'),
    ('done', 'Done'),
    ('error', 'Error'),
] # }}}


class dm_sysmsg(osv.osv): # {{{
    _inherit = "dm.sysmsg"

    _columns = {
       'state': fields.selection(SYSMSG_STATES, 'State to set'),
    }

dm_sysmsg() # }}}


class dm_offer_step_transition(osv.osv): # {{{
    _inherit = "dm.offer.step.transition"

    def unlink(self, cr, uid, ids, context=None):
        def _get_sysmsg(tr_id):
            sysmsg_obj = self.pool.get('dm.sysmsg')
            error_code = 'step_stransition_deleted'
            sysmsg_id = sysmsg_obj.search(cr, uid, [('code', '=', error_code)], context=context)
            if sysmsg_id:
                sysmsg = sysmsg_obj.browse(cr, uid, sysmsg_id, context=context)[0]
                return {
                    'state': sysmsg.state,
                    'error_msg': sysmsg.message + " Transition id: %s" % (tr_id, ),
                }
            else:
                return {
                    'state': 'error',
                    'error_msg': "An unknown error has occured : %s" % (error_code, ),
                }

        workitem_obj = self.pool.get('dm.workitem')
        for idn in ids:
            workitems_to_freeze_ids = workitem_obj.search(cr, uid, [('tr_from_id', '=', idn)])
            vals = _get_sysmsg(idn)
            workitem_obj.write(cr, uid, workitems_to_freeze_ids, vals)

        return super(dm_offer_step_transition, self).unlink(cr, uid, ids, context=context)

dm_offer_step_transition() # }}}

