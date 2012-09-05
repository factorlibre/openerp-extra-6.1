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

import wizard
import pooler

def campaign_partners(self, cr, uid, data, context):
    partner_id = data['id']
    camp_id=[]
    pool = pooler.get_pool(cr.dbname)
    cr.execute("select dcps.id from dm_campaign_proposition_segment dcps, \
                    dm_campaign_proposition dcp, dm_campaign dc where \
                    dcp.id = dcps.proposition_id and dc.id  = dcp.camp_id")
    res = cr.fetchall()
    seg_ids = map(lambda x: x[0], res)
    seg_obj = pool.get('dm.campaign.proposition.segment').browse(cr, uid, seg_ids)
    for seg_id in seg_obj:
        address_ids = seg_id.customers_file_id and seg_id.customers_file_id.address_ids or []
        for address_id in address_ids:
            if partner_id == address_id.partner_id.id:
                camp_id.append(seg_id.campaign_id.id)
    value = {
            'domain': [('id', 'in', camp_id)],
            'name': 'Campaigns',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'dm.campaign',
            'context': { },
            'type': 'ir.actions.act_window'
            }
    return value

class wizard_campaign_partners(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': campaign_partners,
                'state': 'end'
            }
        },
    }
wizard_campaign_partners("wizard_campaign_partners")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: