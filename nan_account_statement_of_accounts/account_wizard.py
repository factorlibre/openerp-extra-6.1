# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2010 NaN Projectes de Programari Lliure, S.L. All Rights Reserved.
#                    http://www.NaN-tic.com
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

import os
import time
import tools
from datetime import datetime
from osv import osv
from osv import fields
from tools.translate import _

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _check_partner(self, account_type, partner_id):
            return account_type in ('payable','receivable') and partner_id or None

    def _balance(self, cr, uid, ids, field_name, arg, context):
        if not ids:
            return {}

        result = {}
        ids = ','.join( [str(int(x)) for x in ids] )

        cr.execute("""
            SELECT 
                aml.id, 
                aml.account_id, 
                aml.partner_id, 
                aml.date, 
                am.name, 
                aml.debit, 
                aml.credit,
                aa.type
            FROM 
                account_move_line aml, 
                account_move am,
                account_account aa
            WHERE 
                aml.account_id = aa.id AND
                aml.move_id = am.id AND 
                aml.id IN (%s)
            """ % ids)
        for record in cr.fetchall():
            id = record[0]
            account_id = record[1]
            partner_id = record[2]
            date = record[3]
            name = record[4]
            debit = record[5] or 0.0
            credit = record[6] or 0.0
            account_type = record[7]

            check_partner = self._check_partner( account_type, partner_id )

            # Order is a bit complex. In theory move lines should be sorted by move_id.name
            # but in some cases move_id will be in draft state and thus move_id.name will be '/'
            # It can also happen that users made some mistakes and move_id.name may be recalculated
            # at the end of the current period or year. So here we consider users want this sorted 
            # by date. In the same date, then then move_id.name is considered and finally if they
            # have the same value, they're sorted by account_move_line.id just to ensure balance
            # is not overlapped.

            # Of course, this filtering criteria must be the one used by the 'search()' function below,
            # so remember to modify that if you want to change this calulation.

            cr.execute("""
                SELECT 
                    SUM(debit-credit)
                FROM 
                    account_move_line aml,
                    account_move am
                WHERE 
                    aml.move_id = am.id AND
                    aml.account_id=%s AND 
                    (%s IS NULL OR aml.partner_id=%s) AND
                    LPAD(EXTRACT(EPOCH FROM aml.date)::VARCHAR, 15, '0') || 
                        LPAD(am.name,15,'0') || 
                        LPAD(aml.id::VARCHAR,15,'0') < 
                    LPAD(EXTRACT(EPOCH FROM %s::DATE)::VARCHAR, 15, '0') || 
                        LPAD(%s,15,'0') || 
                        LPAD(%s::VARCHAR,15,'0')
            """, (account_id,check_partner,partner_id,date,name,id) )
            balance = cr.fetchone()[0] or 0.0
            # Add/substract current debit and credit
            balance += debit - credit
            result[id] = balance
        return result

    _columns = {
        'balance': fields.function(_balance, method=True, string='Balance'),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Override default search function so that if it's being called from the statement of accounts
        tree view, the given order is ignored and a special one is used so it ensures consistency
        between balance field value and account.move.line order.
        """

        if context is None:
            context = {}

        ids = super(account_move_line,self).search(cr, uid, args, offset, limit, order, context, count)

        if isinstance(ids, (long, int)):
            ids = [ids]

        if context.get('statement_of_accounts') and ids:
            # If it's a statement_of_accounts, ignore order given
            ids = ','.join( [str(int(x)) for x in ids] )

            # This sorting criteria must be the one used by the 'balance' functional field above,
            # so remember to modify that if you want to change the order.
            cr.execute("""
                SELECT 
                    aml.id 
                FROM 
                    account_move_line aml, 
                    account_move am 
                WHERE 
                    aml.move_id = am.id AND 
                    aml.id IN (%s) 
                ORDER BY 
                    LPAD(EXTRACT(EPOCH FROM aml.date)::VARCHAR, 15, '0') || 
                        LPAD(am.name,15,'0') || 
                        LPAD(aml.id::VARCHAR,15,'0')
            """ % ids)
            result = cr.fetchall()
            ids = [x[0] for x in result]
        return ids

account_move_line()

class account_statement_accounts_wizard(osv.osv_memory):
    _name = 'account.statement.accounts.wizard'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'account_id': fields.many2one('account.account', 'Account', domain="[('type','!=','view'),('company_id','=',company_id)]", required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return {}

    def action_open(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)


        name = data.partner_id and data.partner_id.name or data.account_id.name
        title = '%s: %s' % (data.account_id.code, name[:10])
        if len(name) > 10:
            title += '...'

        domain = [('account_id', '=', data.account_id.id)]
        if data.partner_id:
            domain += [('partner_id', '=', data.partner_id.id)]


        model_data_ids = self.pool.get('ir.model.data').search(cr,uid, [
            ('model','=','ir.ui.view'),
            ('name','=','account_move_line_statement_of_accounts_view'),
            ('module','=','nan_account_statement_of_accounts'),
        ], context=context)
        resource_id = self.pool.get('ir.model.data').read(cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']
        ctx = context.copy()
        ctx['statement_of_accounts'] = True
        ctx['view_mode'] = True
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(resource_id,'tree'),(False,'form')],
            'context': ctx,
            'domain': domain,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'name': title,
        }

account_statement_accounts_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

