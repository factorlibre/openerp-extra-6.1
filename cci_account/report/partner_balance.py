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
import pooler
import time
from report import report_sxw

class partner_balance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(partner_balance, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'sum_litige': self._sum_litige,
            'sum_sdebit': self._sum_sdebit,
            'sum_scredit': self._sum_scredit,
            'solde_debit': self._solde_balance_debit,
            'solde_credit': self._solde_balance_credit,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
        })

    def set_context(self, objects, data, ids, report_type = None):
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
                context={'fiscalyear': data['form']['fiscalyear']})

        if (data['form']['category'] == 'Customer' ):
            self.ACCOUNT_TYPE = "('receivable')"
        elif (data['form']['category'] == 'Supplier'):
            self.ACCOUNT_TYPE = "('payable')"
        else:
            self.ACCOUNT_TYPE = "('payable','receivable')"
        #
        self.cr.execute("SELECT a.id " \
                "FROM account_account a " \
                "LEFT JOIN account_account_type t " \
                    "ON (a.type = t.code) " \
                "WHERE a.company_id = %s " \
                    "AND a.type IN " + self.ACCOUNT_TYPE + " " \
                    "AND a.active", (data['form']['company_id'],))
        self.account_ids = ','.join([str(a) for (a,) in self.cr.fetchall()])

        self.cr.execute('SELECT DISTINCT line.partner_id ' \
                'FROM account_move_line AS line, account_account AS account ' \
                'WHERE line.partner_id IS NOT NULL ' \
                    'AND line.date >= %s ' \
                    'AND line.date <= %s ' \
                    'AND ' + line_query + ' ' \
                    'AND line.account_id in ('+self.account_ids+') ' \
                    'AND account.company_id = %s ' \
                    'AND account.active ',
                    (data['form']['date1'], data['form']['date2'],
                        data['form']['company_id']))
        new_ids = [id for (id,) in self.cr.fetchall()]

        self.partner_ids = ','.join(map(str, new_ids))
        objects = self.pool.get('res.partner').browse(self.cr, self.uid, new_ids)
        super(partner_balance, self).set_context(objects, data, new_ids, report_type)

    def lines(self):
        if not self.partner_ids:
            return []
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='l',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
            "SELECT p.name, sum(debit) as debit, sum(credit) as credit, " \
                    "CASE WHEN sum(debit) > sum(credit) " \
                        "THEN sum(debit) - sum(credit) " \
                        "ELSE 0 " \
                    "END AS sdebit, " \
                    "CASE WHEN sum(debit) < sum(credit) " \
                        "THEN sum(credit) - sum(debit) " \
                        "ELSE 0 " \
                    "END AS scredit, " \
                    "(SELECT sum(debit-credit) " \
                        "FROM account_move_line l " \
                        "WHERE partner_id = p.id " \
                            "AND date >= %s " \
                            "AND date <= %s " \
                            "AND blocked = TRUE " \
                            "AND " + line_query + " " \
                    ") AS enlitige " \
            "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
            "WHERE "
                "account_id IN (" + self.account_ids + ") " \
                "AND partner_id is not null " \
                "AND l.date >= %s " \
                "AND l.date <= %s " \
                "AND " + line_query + " " \
            "GROUP BY p.id, p.name " \
            "ORDER BY  p.name ",
            (self.datas['form']['date1'], self.datas['form']['date2'],
                self.datas['form']['date1'], self.datas['form']['date2']))
        res = self.cr.dictfetchall()
        return res

    def _sum_debit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                'SELECT sum(debit) ' \
                'FROM account_move_line ' \
                'WHERE ' \
                    'account_id IN (' + self.account_ids + ') ' \
                    "AND partner_id is not null " \
                    'AND date >=%s ' \
                    'AND date <= %s ' \
                    'AND ' + line_query,
            (self.datas['form']['date1'], self.datas['form']['date2']))
        return self.cr.fetchone()[0] or 0.0

    def _sum_credit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                'SELECT sum(credit) ' \
                'FROM account_move_line ' \
                'WHERE '
                    'account_id IN (' + self.account_ids + ') ' \
                    "AND partner_id is not null " \
                    'AND date >= %s ' \
                    'AND date <= %s ' \
                    'AND ' + line_query,
                (self.datas['form']['date1'], self.datas['form']['date2']))
        return self.cr.fetchone()[0] or 0.0

    def _sum_litige(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                'SELECT sum(debit-credit) ' \
                'FROM account_move_line ' \
                'WHERE ' \
                    'account_id IN (' + self.account_ids + ') ' \
                    "AND partner_id is not null " \
                    'AND date >= %s ' \
                    'AND date <= %s ' \
                    'AND blocked=TRUE ' \
                    'AND ' + line_query,
                (self.datas['form']['date1'], self.datas['form']['date2']))
        return self.cr.fetchone()[0] or 0.0

    def _sum_sdebit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
            'SELECT CASE WHEN sum(debit) > sum(credit) ' \
                    'THEN sum(debit - credit) ' \
                    'ELSE 0 ' \
                'END ' \
            'FROM account_move_line ' \
            'WHERE ' \
                'account_id IN (' + self.account_ids + ') ' \
                "AND partner_id is not null " \
                'AND date >= %s ' \
                'AND date <= %s ' \
                'AND ' + line_query + ' ' \
            'GROUP BY partner_id',
            (self.datas['form']['date1'], self.datas['form']['date2']))
        return self.cr.fetchone()[0] or 0.0

    def _sum_scredit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
            'SELECT CASE WHEN sum(debit) < sum(credit) ' \
                    'THEN sum(credit - debit) ' \
                    'ELSE 0 ' \
                'END ' \
            'FROM account_move_line ' \
            'WHERE '
                'account_id IN (' + self.account_ids + ') ' \
                "AND partner_id is not null " \
                'AND date >= %s ' \
                'AND date <= %s ' \
                'AND ' + line_query + ' ' \
            'GROUP BY partner_id',
            (self.datas['form']['date1'], self.datas['form']['date2']))
        return self.cr.fetchone()[0] or 0.0

    def _solde_balance_debit(self):
        debit, credit = self._sum_debit(), self._sum_credit()
        return debit > credit and debit - credit

    def _solde_balance_credit(self):
        debit, credit = self._sum_debit(), self._sum_credit()
        return credit > debit and credit - debit

    def _get_company(self, form):
        return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).name

    def _get_currency(self, form):
        return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.name

report_sxw.report_sxw('report.partner.balance', 'res.partner',
    'addons/cci_account/report/partner_balance.rml',parser=partner_balance,
    header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

