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
import time
from report import report_sxw

class carnet_before_validity(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(carnet_before_validity, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'carnet_before': self._carnet_before,
        })

    def _carnet_before(self):
        import mx.DateTime as dt
        res = {}
        res_list = []
        today = dt.now()
        before_date = dt.now() + dt.RelativeDateTime(months=1)
        before_date  = before_date.strftime("%Y-%m-%d")
        today = today.strftime("%Y-%m-%d")
        carnet_obj = self.pool.get('cci_missions.ata_carnet')
        carnet_ids = carnet_obj.search(self.cr, self.uid, [('validity_date', '<=', before_date),('validity_date','>=',today), ('state', '>=', 'created')])
        carnet_data = carnet_obj.browse(self.cr, self.uid, carnet_ids)
        for carnet in carnet_data:
            flag = False
            address = ''
            for letter in carnet.letter_ids:
                if letter.letter_type == 'Rappel avant echeance':
                    flag = True
            if not flag:
                if carnet.partner_id.address:
                    for add in carnet.partner_id.address:
                        if add.type=='default':
                            address = (add.street or '') + ' ' + (add.street2 or '') + '\n' + (add.zip_id and add.zip_id.name or '') + ' ' + (add.city or '')  + '\n' + (add.state_id and add.state_id.name or '') + ' ' + (add.country_id and add.country_id.name or '')
                            continue
                        else:
                            address = (add.street or '') + ' ' + (add.street2 or '') + '\n' + (add.zip_id and add.zip_id.name or '') + ' ' + (add.city or '')  + '\n' + (add.state_id and add.state_id.name or '') + ' ' + (add.country_id and add.country_id.name or '')
                res = { 'partner_name': carnet.partner_id.name,
                        'partner_address': address,
                        'type': carnet.type_id.name,
                        'name': carnet.name,
                        'creation_date': carnet.creation_date,
                        'validity_date': carnet.validity_date
                      }
                res_letter = {
                      'letter_type': 'Rappel avant echeance',
                      'date': time.strftime('%Y-%m-%d'),
                      'ata_carnet_id': carnet.id,
                              }
                id = self.pool.get('cci_missions.letters_log').create(self.cr, self.uid, res_letter)
                res_list.append(res)
        return res_list

report_sxw.report_sxw('report.carnet.before.validity', 'cci_missions.ata_carnet', 'addons/cci_mission/report/carnet_before_validity.rml', parser=carnet_before_validity, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
