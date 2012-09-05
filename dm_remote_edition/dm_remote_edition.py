# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

class dm_campaign_document_job(osv.osv): # {{{
    _inherit = "dm.campaign.document.job"
    
    _columns = {
         'user_id': fields.many2one('res.users', 'Printer User'),
        }
dm_campaign_document_job() # }}}


class dm_campaign_document_job_batch(osv.osv): # {{{
    _inherit = "dm.campaign.document.job.batch"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.has_key('portal_dm') and context['portal_dm']=='service':
            cr.execute("select batch_id from dm_campaign_document_job where batch_id in (select id from dm_campaign_document_job_batch) and user_id = %s" %(uid))
            batch_ids = map(lambda x: x[0], cr.fetchall())
            return batch_ids
        return super(dm_campaign_document_job_batch, self).search(cr, uid, args, offset, limit, order, context, count)

dm_campaign_document_job_batch() # }}}			   		    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
