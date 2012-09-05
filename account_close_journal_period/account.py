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

from osv import osv
from osv import fields

class account_journal_period(osv.osv):
    '''
    Module that allows to close a particular journal of a given period
    '''
    _inherit = 'account.journal.period'

    def action_draft(self, cr, uid, ids, *args):
        mode = 'draft'
        journal_periods = self.browse(cr, uid, ids)
        for journal_period in journal_periods:
            cr.execute('update account_journal_period set state=%s where id=%s', (mode, journal_period.id))
            cr.execute('update account_period set state=%s where id=%s', (mode, journal_period.period_id.id))
        return True

account_journal_period()
