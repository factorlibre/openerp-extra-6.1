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

class crm_case(osv.osv): # {{{
    _inherit = "crm.case"
    
    _columns = {
        'segment_id': fields.many2one('dm.campaign.proposition.segment', 'Segment')
        }
crm_case() # }}}

class dm_campaign_proposition(osv.osv):#{{{
    _inherit = "dm.campaign.proposition"

    def create(self,cr,uid,vals,context={}):
        if 'camp_id' in vals and vals['camp_id'] :
            camp_id = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
            ''' Create CRM Section '''
            crm_obj = self.pool.get('crm.case.section')
            crm_id = crm_obj.search(cr, uid, [('name', '=', camp_id.name)])
            if crm_id:
                section_vals = {
                        'name': vals['name'],
                        'parent_id': crm_id[0],
                        }
                crm_obj.create(cr,uid,section_vals)
        return super(dm_campaign_proposition, self).create(cr, uid, vals, context)

dm_campaign_proposition() #}}}

class dm_campaign(osv.osv):#{{{
    _inherit = "dm.campaign"

    def create(self, cr, uid, vals, context={}):
        id_camp = super(dm_campaign, self).create(cr, uid, vals, context)
        data_camp = self.browse(cr, uid, id_camp)
        ''' Create CRM Section '''
        crm_obj = self.pool.get('crm.case.section')
        crm_id = crm_obj.search(cr, uid, [('code', 'ilike', 'DM')])
        if crm_id:
            section_vals = {
                    'name': data_camp.name,
                    'parent_id': crm_id[0],
                }
            crm_obj.create(cr, uid, section_vals)
        return id_camp

dm_campaign()  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
