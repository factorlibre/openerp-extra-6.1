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
import netsvc
from osv import fields, osv
import ir
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime
from tools import config

class account_account(osv.osv):
    _inherit="account.account"

    def _get_account_values(self, cr, uid, id, accounts, field_names, context={}):
        res = {}.fromkeys(field_names, 0.0)
        browse_rec = self.browse(cr, uid, id)
        if browse_rec.type == 'consolidation':
            ids2 = self.read(cr, uid, [browse_rec.id], ['child_consol_ids'], context)[0]['child_consol_ids']
            for t in self.search(cr, uid, [('parent_id', 'child_of', [browse_rec.id])]):
                if t not in ids2 and t != browse_rec.id:
                    ids2.append(t)
            for i in ids2:
                tmp = self._get_account_values(cr, uid, i, accounts, field_names, context)
                for a in field_names:
                    res[a] += tmp[a]
        else:
            ids2 = self.search(cr, uid, [('parent_id', 'child_of', [browse_rec.id])])
            for i in ids2:
                for a in field_names:
                    res[a] += accounts.get(i, {}).get(a, 0.0)
        return res
        
    def compute_total(self, cr, uid, ids, yr_st_date, yr_end_date, st_date, end_date, field_names, context={}):
        if not (st_date >= yr_st_date and end_date <= yr_end_date):
            return {}
        #compute the balance/debit/credit accordingly to the value of field_name for the given account ids
        mapping = {
            'balance': "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance ",
            'debit': "COALESCE(SUM(l.debit), 0) as debit ",
            'credit': "COALESCE(SUM(l.credit), 0) as credit "
        }
        #get all the necessary accounts
        ids2 = self._get_children_and_consol(cr, uid, ids, context)
        acc_set = ",".join(map(str, ids2))

        accounts = {}
        if ids2:
            query = self.pool.get('account.move.line')._query_get(cr, uid,
                    context=context)
            cr.execute("SELECT l.account_id as id, "  \
                    +  ' , '.join(map(lambda x: mapping[x], field_names.keys() ))  + \
                    "FROM account_move_line l " \
                    "WHERE l.account_id IN ("+ acc_set +") " \
                        "AND " + query + " " \
                        " AND l.date >= "+"'"+ st_date +"'"+" AND l.date <= "+"'"+ end_date +""+"'"" " \
                    "GROUP BY l.account_id ")
            for res in cr.dictfetchall():
                accounts[res['id']] = res
        #for the asked accounts, get from the dictionnary 'accounts' the value of it
        res = {}
        for id in ids:
            res[id] = self._get_account_values(cr, uid, id, accounts, field_names, context)
        return res

account_account()