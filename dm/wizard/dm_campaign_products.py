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

def products_campaign(self, cr, uid, data, context):
    product_id = data['id']
    pool = pooler.get_pool(cr.dbname)
    camp_pro_item_ids = pool.get('dm.campaign.proposition.item').search(cr, uid, 
                                               [('product_id', '=', product_id)])
    
    camp_pro_id = []
    for item_id in camp_pro_item_ids:
        item = pool.get('dm.campaign.proposition.item').browse(cr, uid, item_id)
        if item.proposition_id and item.proposition_id.camp_id:
            camp_pro_id.append(item.proposition_id.camp_id.id)
    value = {
    'domain': [('id', 'in', camp_pro_id)],
    'name': 'Campaigns',
    'view_type': 'form',
    'view_mode': 'tree,form',
    'res_model': 'dm.campaign',
    'context': { },
    'type': 'ir.actions.act_window'
            }
    return value

class wizard_products_campaign(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': products_campaign,
                'state': 'end'
            }
        },
    }
wizard_products_campaign("wizard_products_campaign")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
