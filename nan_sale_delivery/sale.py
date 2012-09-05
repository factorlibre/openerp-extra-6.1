##############################################################################
#
# Copyright (c) 2011  NaN Projectes de Programari Lliure, S.L. - All Rights Reserved.
#                     http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv
import time
import datetime
from datetime import date, timedelta

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _delay_calculation(self, cr, uid, ids, field_name, field_value, context):
        result = {}
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for line in self.browse(cr, uid, ids, context=context):
            date_planned = datetime.datetime.strptime(line.date_planned,'%Y-%m-%d %H:%M:%S')
            delay = date_planned - datetime.datetime.now() 
            #adding company security lead days (correction for date_expected on stock_moves)
            delay += timedelta(days=company.security_lead)
            #convert delay on days (1 day = 86400 seconds)
            result[line.id] = delay.days + (delay.seconds / 86400.0)

        return result

    _columns = {
        'date_planned': fields.datetime('Delivery date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'delay': fields.function(_delay_calculation, method=True, type="float", string='Calculated delay'),  
    }

    _defaults = {
        'date_planned': lambda *a: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
sale_order_line()
