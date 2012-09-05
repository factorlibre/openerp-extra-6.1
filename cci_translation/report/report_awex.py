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

import time
from report import report_sxw
from osv import osv

class translation_awex(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(translation_awex, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_objects': self._get_objects
        })

    def _get_objects(self, data):
        val = []
        res = {}
        seq = 0
        folder_obj = self.pool.get('translation.folder')
        self.cr.execute("select id from translation_folder where awex_eligible=True AND state='confirmed' \
            AND (order_date BETWEEN '%s' AND '%s' )" % (data['date_from'], data['date_to']))

        lines = map(lambda x:folder_obj.browse(self.cr, self.uid,x[0]), self.cr.fetchall())
        for line in lines:
            seq +=1
            res = {}
            res['number'] = seq
            res['date'] = line.order_date
            res['obj_name'] = 'Translation'
            res['obj_id'] = line.id
            res['partner'] = line.partner_id.name
            res['desc'] = line.name
            res['inv_num'] = line.invoice_id.number
            res['amt'] = line.awex_amount
            val.append(res)

        folder_obj = self.pool.get('cci_missions.embassy_folder_line')
        self.cr.execute("select l.id from cci_missions_embassy_folder_line l\
            join cci_missions_embassy_folder f on (f.id=l.folder_id)\
            join crm_case c on (c.id=f.crm_case_id)\
            where l.awex_eligible=True and \
            l.type='Translation' and \
            c.state='open' and \
            (f.create_date::date BETWEEN '%s' AND '%s' )" % (data['date_from'], data['date_to']))
        lines1 = map(lambda x:folder_obj.browse(self.cr, self.uid,x[0]), self.cr.fetchall())
        for line in lines1:
            seq +=1
            res = {}
            res['number'] = int(seq)
            res['date'] = time.strftime('%Y-%m-%d', time.strptime(line.folder_id.create_date, '%Y-%m-%d %H:%M:%S' ))
            res['obj_name'] = 'Embassy folder line'
            res['obj_id'] = int(line.id)
            res['partner'] = ((line.folder_id.crm_case_id and \
                            line.folder_id.crm_case_id.partner_id and \
                            line.folder_id.crm_case_id.partner_id.name) or '')
            res['desc'] = line.name
            res['inv_num'] = ((line.folder_id.invoice_id and line.folder_id.invoice_id.number) or '')
            res['amt'] = line.customer_amount
            val.append(res)
        return val

    def _statastics_details(self):
        lines = []
        return lines

report_sxw.report_sxw(
    'report.translation.awex',
    'translation.folder',
    'addons/cci_translation/report/report_awex.rml',
    parser=translation_awex, header=False
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
