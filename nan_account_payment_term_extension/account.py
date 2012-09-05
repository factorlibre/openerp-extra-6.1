##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import fields, osv


class account_payment_term(osv.osv):
    _inherit="account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        """
        This function is a copy of account.payment.term compute() function but it adds the possibility 
        of using 'division' value in 'value' field and also honours the value in 'months' field.
        """
        if isinstance(id, list):
            id = id[0]
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            elif line.value == 'division':
                amt = round(value / line.value_amount, prec)
            if amt:
                next_date = datetime.strptime(date_ref, '%Y-%m-%d') 
		# Add months first
		next_date += relativedelta(months=line.months or 0)
		# Add days later
                next_date += relativedelta(days=line.days)
                if line.days2 < 0:
                    next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days2)
                if line.days2 > 0:
                    next_date += relativedelta(day=line.days2, months=1)
                result.append( (next_date.strftime('%Y-%m-%d'), amt) )
                amount -= amt
        return result

account_payment_term()

class account_payment_term_line(osv.osv):
    _inherit = 'account.payment.term.line'

    _columns = {
        'months': fields.integer('Number of Months', help="Number of months to add to invoice date."),
        'value': fields.selection([
            ('procent', 'Percent'),
            ('balance', 'Balance'),
            ('fixed', 'Fixed Amount'),
            ('division', 'Division'),
            ], 'Valuation', required=True, help="Select here the kind of valuation related to this payment term line. Note that you should have your last line with the type 'Balance' to ensure that the whole amount will be threated."),
        'value_amount': fields.float('Value Amount', digits=(12,4), help="For Value percent enter % ratio between 0-1."),
    }
account_payment_term_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
