# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account reversal module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#    with the kind advice of Nicolas Bessi from Camptocamp
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

from osv import fields, osv
from tools.translate import _

class account_move(osv.osv):
    _inherit = "account.move"

    def create_reversal(self, cr, uid, ids, reversal_date, reversal_ref_prefix=False, reversal_line_prefix=False, reconcile=True, context=None):
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        reversed_move_ids = []
        for src_move in self.browse(cr, uid, ids, context=context):
            # since OpenERP v6, we have company_id on account.move
            if self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', 'company_id'), ('model', '=', 'account.move')], context=context) != []:
                context['company_id'] = src_move.company_id.id
            # With the additions in this branch
            # https://code.launchpad.net/~openerp-dev/openobject-addons/6.0-opw-5852-pso/+merge/66682
            # which is not merged yet into openobject-addons as of 27/7/2011
            # calling find() on accout.period will take the company into account if
            # company_id is in the context
            reversal_move_id = self.copy(cr, uid, src_move.id,
                default={
                    'date': reversal_date,
                    'period_id': self.pool.get('account.period').find(cr, uid, reversal_date, context=context)[0],
                    'ref': ''.join([x for x in [reversal_ref_prefix, src_move.ref] if x]),
                 }, context=context)
            reversed_move_ids.append(reversal_move_id)
            reversal_move = self.browse(cr, uid, reversal_move_id, context=context)
            for reversal_move_line in reversal_move.line_id:
                move_line_obj.write(cr, uid, [reversal_move_line.id], {
                    'debit': reversal_move_line.credit,
                    'credit': reversal_move_line.debit,
                    'amount_currency': reversal_move_line.amount_currency * -1,
                    'name': ' '.join([x for x in [reversal_line_prefix, reversal_move_line.name] if x]),
                        }, context=context, check=True, update_check=True)

            # re-generate analytic lines for moves with validate function
            self.validate(cr, uid, [reversal_move_id], context=context)
            if reconcile:
                for src_move_line in src_move.line_id:
                    if not src_move_line.account_id.reconcile and not src_move_line.reconcile_id:
                        continue
                    else:
                        for reversal_move_line in reversal_move.line_id:
                            # Given that we are in a wizard, the move_line_obj.write that we
                            # performed above will not be taken into account until the
                            # end of the wizard => debit and credit are still not swapped
                            # in the reversal move
                            if reversal_move_line.account_id == src_move_line.account_id and reversal_move_line.credit == src_move_line.credit and reversal_move_line.debit == src_move_line.debit and not reversal_move_line.reconcile_id:
                                move_line_obj.reconcile(cr, uid, [src_move_line.id, reversal_move_line.id], context=context)
        return reversed_move_ids

account_move()


class account_reversal_wizard(osv.osv_memory):
    _name = "account.reversal.wizard"
    _description = "Wizard to reverse an account move"
    _columns = {
        'reversal_date': fields.date('Date of reversals', required=True, help="Enter the date of the reversal account moves. By default, OpenERP proposes the first day of the next period."),
        'reversal_ref_prefix': fields.char('Prefix for Ref of reversal moves', size=32, help="Prefix that will be added to the 'Ref' of the original account moves to create the 'Ref' of the reversal moves (no space added after the prefix)."),
        'reversal_line_prefix': fields.char('Prefix for Name of reversal move lines', size=32, help="Prefix that will be added to the name of the original account move lines to create the name of the reversal move lines (a space is added after the prefix)."),
        'reversal_reconcile': fields.boolean('Reconcile reversals', help="If active, the reversal account moves will be reconciled with the original account moves."),
        }


    def _first_day_next_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        first_day_next_period = False
        if context.get('active_ids', False):
            period_src = self.pool.get('account.move').browse(cr, uid, context['active_ids'][0], context=context).period_id
            period_reversal_id = self.pool.get('account.period').next(cr, uid, period_src, 1, context=context)
            first_day_next_period = self.pool.get('account.period').read(cr, uid, period_reversal_id, ['date_start'], context=context)['date_start']
        return first_day_next_period

    _defaults = {
        'reversal_date': _first_day_next_period,
        'reversal_line_prefix': lambda *a: 'REV -',
        'reversal_reconcile': lambda *a: True,
        }


    def start_wizard_reversal(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = self.read(cr, uid, ids)[0]
        # WARNING : if the user is in the tree view and doesn't select any line,
        # context['active_ids'] contains all the lines of the tree view
        if context.get('active_ids', False):
            reversed_move_ids = self.pool.get('account.move').create_reversal(cr, uid, context['active_ids'], res['reversal_date'], res['reversal_ref_prefix'], res['reversal_line_prefix'], reconcile=res['reversal_reconcile'], context=context)
            return {
                'name': 'Reversal account moves',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': reversed_move_ids,
                }
        else:
            return True

account_reversal_wizard()
