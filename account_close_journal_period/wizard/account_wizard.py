# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields, osv

class account_journal_period_close(osv.osv_memory):
    """
        close journal period
    """
    _name = "account.journal.period.close"
    _description = "journal period close"
    _columns = {
        'sure': fields.boolean('Check this box'),
    }

    def data_save(self, cr, uid, ids, context=None):
        """
        This function close journal period
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: account period close’s ID or list of IDs
         """
        
        journal_period_pool = self.pool.get('account.journal.period')
        mode = 'done'
        for form in self.read(cr, uid, ids, context=context):
            if form['sure']:
                for id in context['active_ids']:
                    cr.execute('update account_journal_period set state=%s where id=%s', (mode, id))

                    journal_period = journal_period_pool.browse(cr, uid, id)
                    period_id = journal_period.period_id.id
                    journal_period_ids = journal_period_pool.search(cr, uid, [('period_id','=',period_id)])
                    journal_periods = journal_period_pool.browse(cr, uid, journal_period_ids)
                    period_close = reduce(lambda x, y: x and y, [x.state==mode for x in journal_periods])
                    if period_close:
                        cr.execute('update account_period set state=%s where id=%s', (mode, period_id))

        return {}

account_journal_period_close()
