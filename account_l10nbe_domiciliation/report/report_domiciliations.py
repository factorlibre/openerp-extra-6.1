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

class invoice_domiciliations(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_domiciliations, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'invoice_details' : self._get_invoice_details,
            'statastics_details' : self._statastics_details,
        })

    def _get_invoice_details(self, inv_ids):
        lines = []
        inv_obj = self.pool.get('account.invoice')
        for inv in inv_obj.browse(self.cr, self.uid, inv_ids):
            res = {}
            res['client'] = inv.partner_id.name
            res['number'] = inv.partner_id.domiciliation
            res['bank'] = inv.partner_id.bank_ids and (inv.partner_id.bank_ids[0].bank and inv.partner_id.bank_ids[0].bank.name or '') or ''
            res['amount'] = (inv.type == 'out_refund') and -inv.residual or inv.residual
            res['communication'] = inv.name or ''  
            lines.append(res)
        return lines
    
    def _statastics_details(self, bank_account_id, inv_ids):
        lines = []
        datas = ['rec_bank_tot', 'rec_bank_val', 'ref_bank_tot', 'ref_bank_val' , \
                                          'rec_other_tot', 'rec_other_val', 'ref_other_tot', 'ref_other_val' ]
        res = {}
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        bank = self.pool.get('res.partner.bank').browse(self.cr, self.uid, bank_account_id)
        res['bank_name'] = ''
        if not bank.bank:
            bank_id = '0'
        else:
            bank_id = str(bank.bank.id)
            res['bank_name'] = bank.bank.name
        invoice_ids = ','.join(map(str,inv_ids)) 
        self.cr.execute("select count(id) as tot, coalesce(sum(residual),0)as val from account_invoice \
                    where partner_id in (select p.id from res_partner p \
                        join res_partner_bank a on (a.partner_id=p.id)\
                         join res_bank b on (b.id=a.bank) where b.id =%s) \
                             and type not like '%%refund' \
                             and id in (%s)" % (bank_id,invoice_ids))
        val1= self.cr.dictfetchall()
        if val1:
            res['rec_bank_tot'] = val1[0]['tot'] # 1
            res['rec_bank_val'] = val1[0]['val'] # 2
        

        self.cr.execute("select count(id) as tot, coalesce(sum(residual),0)as val from account_invoice \
                    where partner_id in (select p.id from res_partner p \
                        join res_partner_bank a on (a.partner_id=p.id)\
                         join res_bank b on (b.id=a.bank) where b.id =%s) \
                             and type like '%%refund' \
                             and id in (%s)" % (bank_id,invoice_ids))
        val2= self.cr.dictfetchall()
        if val2:
            res['ref_bank_tot'] = val2[0]['tot'] # 5
            res['ref_bank_val'] = val2[0]['val'] # 6
        
        self.cr.execute("select count(id) as tot, coalesce(sum(residual),0)as val from account_invoice \
                    where partner_id in (select p.id from res_partner p \
                        join res_partner_bank a on (a.partner_id=p.id)\
                         join res_bank b on (b.id=a.bank) where b.id !=%s) \
                             and type not like '%%refund' \
                             and id in (%s)" % (bank_id,invoice_ids))
        val3= self.cr.dictfetchall()
        if val3:
            res['rec_other_tot'] = val3[0]['tot'] # 3
            res['rec_other_val'] = val3[0]['val'] # 4
       
        self.cr.execute("select count(id) as tot, coalesce(sum(residual),0)as val from account_invoice \
                    where partner_id in (select p.id from res_partner p \
                        join res_partner_bank a on (a.partner_id=p.id)\
                         join res_bank b on (b.id=a.bank) where b.id !=%s) \
                             and type like '%%refund' \
                             and id in (%s)" % (bank_id,invoice_ids))
        val4= self.cr.dictfetchall()
        if val4:
            res['ref_other_tot'] = val4[0]['tot'] # 7
            res['ref_other_val'] = val4[0]['val'] # 8

        for d in datas:
            res.setdefault(0.0)

        lines.append(res)
        return lines

report_sxw.report_sxw(
    'report.invoice.domiciliation.dom',
    'account.invoice',
    'addons/account_l10nbe_domiciliation/report/domiciliations.rml',
    parser=invoice_domiciliations, header=False
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
