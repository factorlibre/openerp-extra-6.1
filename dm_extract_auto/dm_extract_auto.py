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
from osv import fields
from osv import osv
import time
import datetime

import time
import datetime
import netsvc

UNITS_DELAY = [
        ('minutes', 'Minutes'),
        ('hours','Hours'),
        ('days','Days'),
        ('weeks','Weeks'),
        ('months','Months')
        ]
        
class dm_campaign_proposition_segment(osv.osv):
    _name = "dm.campaign.proposition.segment"
    _description = "Segmentation"
    _inherit = "dm.campaign.proposition.segment"
    
    def onchange_extract_date_start(self, cr, uid, ids, extract_date_start, extract_delay, extract_unit_delay):
        if extract_date_start and extract_unit_delay:
            params = {(extract_unit_delay): extract_delay}
            for unit, value in params.items():
                if unit == 'months':
                    extract_date_next = datetime.datetime.strptime(extract_date_start, '%Y-%m-%d  %H:%M:%S') + datetime.timedelta(value*365/12)
                else:
                    extract_date_next = datetime.datetime.strptime(extract_date_start, '%Y-%m-%d  %H:%M:%S') + datetime.timedelta(**params)
            return {'value': {'extract_date_next': extract_date_next.strftime('%Y-%m-%d %H:%M:%S')}}
        else:
            return {'value': {}}
       
    _columns = {
            'auto_extract': fields.boolean('Use Automatic Extraction'),
            'extract_date_start': fields.datetime('First Extraction Date'),
            'extract_date_end': fields.datetime('Last Extraction Date'),
            'extract_date_previous': fields.datetime('Previous Extraction Date', readonly=True),
            'extract_date_next': fields.datetime('Next Extraction Date'),
            'extract_delay': fields.integer('Delay'),
            'extract_unit_delay': fields.selection(UNITS_DELAY, 'Delay Unit'),
                }

    def check_auto_extract(self, cr, uid, ids=False, context={}):
        seg_ids = self.search(cr, uid, [('extract_date_next', '<=', time.strftime('%Y-%m-%d %H:%M:%S'))])
        for seg_id in seg_ids:
            seg_obj = self.browse(cr, uid, [seg_id])[0]
            if seg_obj.segmentation_id.id:
                name = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + str(seg_obj.name)
                code = time.strftime('%Y-%m-%d %H:%M:%S') + '_' + str(seg_obj.code) or '' 
                wizard_service = netsvc.LocalService("wizard")
                passwd = self.pool.get('res.users').browse(cr, uid, uid).password
                wizard_res = wizard_service.create(cr.dbname, uid, passwd, 'wizard.extract.customer')
                datas = {'form': {'code': code, 'name': name}, 'ids': [seg_obj.segmentation_id.id], 'report_type': 'pdf', 'model': 'dm.address.segmentation', 'id': seg_obj.segmentation_id.id}
                state = 'ok'
                res3 = wizard_service.execute(cr.dbname, uid, passwd, wizard_res , datas, state, {})
                #TODO raise exception for delay
                if not seg_obj.extract_unit_delay:
                    return False
                ext_delay_params = {(str(seg_obj.extract_unit_delay)): seg_obj.extract_delay}
                for unit, value in ext_delay_params.items():
                    if unit == 'months':
                        extr_next_date = datetime.datetime.strptime(seg_obj.extract_date_next, '%Y-%m-%d  %H:%M:%S') + datetime.timedelta(value*365/12)
                    else:
                        extr_next_date = datetime.datetime.strptime(seg_obj.extract_date_next, '%Y-%m-%d  %H:%M:%S') + datetime.timedelta(**ext_delay_params)
                self.write(cr, uid, [seg_id], {'extract_date_previous': seg_obj.extract_date_next,
                                              'extract_date_next': extr_next_date})
    
dm_campaign_proposition_segment()

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
