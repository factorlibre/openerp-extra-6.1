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

import time
from report import report_sxw
from tools import amount_to_text_en
from osv import osv

class sale_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
        })
    def convert(self,amount, cur):
        cur=cur.name
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return amt_en
    
report_sxw.report_sxw('report.sale.order.india','sale.order','addons/sale_numbers/report/sale_order.rml',parser=sale_order, header=False)
