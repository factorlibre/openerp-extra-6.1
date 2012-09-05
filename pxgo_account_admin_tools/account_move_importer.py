import netsvc
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Pexego Sistemas Informáticos. All Rights Reserved
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
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

"""
Account Move Importer
"""
__author__ = "Borja López Soilán (Pexego)"

import time
import csv
import base64
import StringIO
import re
from osv import fields, osv
from tools.translate import _

class pxgo_account_move_importer(osv.osv_memory):
    """
    Account Move Importer

    Wizard that imports a CSV file into a new account move.

    The CSV file is expected to have at least the account code, a reference
    (description of the move line), the debit and the credit.

    The lines of the CSV file are tested to be valid account move lines
    using the regular expresions set on the wizard.
    """
    _name = "pxgo_account_admin_tools.pxgo_account_move_importer"
    _description = "Account move importation wizard"

    _columns = {
        #
        # Account move parameters
        #
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'ref': fields.char('Ref', size=64, required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'date': fields.date('Date', required=True),

        'type': fields.selection([
            ('pay_voucher', 'Cash Payment'),
            ('bank_pay_voucher', 'Bank Payment'),
            ('rec_voucher', 'Cash Receipt'),
            ('bank_rec_voucher', 'Bank Receipt'),
            ('cont_voucher', 'Contra'),
            ('journal_sale_vou', 'Journal Sale'),
            ('journal_pur_voucher', 'Journal Purchase'),
            ('journal_voucher', 'Journal Voucher'),
        ], 'Type', select=True, required=True),

        #
        # Input file
        #
        'input_file': fields.binary('File', filters="*.csv", required=True),
        'input_file_name': fields.char('File name', size=256),
        'csv_delimiter': fields.char('Delimiter', size=1, required=True),
        'csv_quotechar': fields.char('Quote', size=1, required=True),
        'csv_decimal_separator': fields.char('Decimal sep.', size=1, required=True),
        'csv_thousands_separator': fields.char('Thousands sep.', size=1, required=True),

        'csv_code_index': fields.integer('Code field', required=True),
        'csv_code_regexp': fields.char('Code regexp', size=32, required=True),
        'csv_ref_index': fields.integer('Ref field', required=True),
        'csv_ref_regexp': fields.char('Ref regexp', size=32, required=True),
        'csv_debit_index': fields.integer('Debit field', required=True),
        'csv_debit_regexp': fields.char('Debit regexp', size=32, required=True),
        'csv_credit_index': fields.integer('Credit field', required=True),
        'csv_credit_regexp': fields.char('Credit regexp', size=32, required=True),
        'csv_partner_ref_index': fields.integer('Partner Ref field', required=True),
        'csv_partner_ref_regexp': fields.char('Partner Ref regexp', size=32, required=True),
        'oerp_partner_ref_field': fields.many2one('ir.model.fields',
                'OpenERP Partner field', required=True,
                domain=[
                    ('model', '=', 'res.partner'),
                    '|',
                    ('ttype', '=', 'char'),
                    ('ttype', '=', 'many2one')
                ]),
    }


    def _get_default_period_id(self, cr, uid, context=None):
        """
        Returns the default period to use (based on account.move)
        """
        period_ids = self.pool.get('account.period').find(cr, uid)
        return period_ids and period_ids[0] or False

    def _get_default_ref_field(self, cr, uid, ids, context=None):
        """ This method set the default value to ref field in res.partner model
            for the oerp_partner_ref_field field
            @param self: The object pointer
            @param cr: The current row, from the database cursor,
            @param uid: The current user’s ID for security checks,
            @param ids: List of registers’ IDs
            @param context: A standard dictionary for contextual values
            @return: return default value
        """
        if context is None:
            context = {}
        model_field_obj = self.pool.get('ir.model.fields')
        model_field_ids = model_field_obj.search(cr,
                uid, [
                    ('model', '=', 'res.partner'),
                    ('name', '=', 'ref')
                ], context)
        default_model_field = model_field_obj.browse(cr, uid, model_field_ids,
                context)[0].id
        return default_model_field

    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id,
        'period_id': _get_default_period_id,
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'type': lambda * a: 'journal_voucher', # Based on account move
        'csv_delimiter': lambda * a: ';',
        'csv_quotechar': lambda * a: '"',
        'csv_decimal_separator': lambda * a: '.',
        'csv_thousands_separator': lambda * a: ',',
        'csv_code_index': lambda * a: 0,
        'csv_ref_index': lambda * a: 1,
        'csv_debit_index': lambda * a: 2,
        'csv_credit_index': lambda * a: 3,
        'csv_partner_ref_index': lambda * a: 4,
        'csv_code_regexp': lambda * a: r'^[0-9]+$',
        'csv_ref_regexp': lambda * a: r'^.*$',
        'csv_partner_ref_regexp': lambda * a: r'^.*$',
        'csv_debit_regexp': lambda * a: r'^[0-9\-\.\,]*$',
        'csv_credit_regexp': lambda * a: r'^[0-9\-\.\,]*$',
        'oerp_partner_ref_field': _get_default_ref_field,
    }


    def _get_accounts_map(self, cr, uid, context=None):
        """
        Find the receivable/payable accounts that are associated with
        a single partner and return a (account.id, partner.id) map
        """
        partner_ids = self.pool.get('res.partner').search(cr, uid, [], context=context)
        accounts_map = {}
        for partner in self.pool.get('res.partner').browse(cr, uid, partner_ids, context=context):
            #
            # Add the receivable account to the map
            #
            if accounts_map.get(partner.property_account_receivable.id, None) is None:
                accounts_map[partner.property_account_receivable.id] = partner.id
            else:
                # Two partners with the same receivable account: ignore
                # this account!
                accounts_map[partner.property_account_receivable.id] = 0
            #
            # Add the payable account to the map
            #
            if accounts_map.get(partner.property_account_payable.id, None) is None:
                accounts_map[partner.property_account_payable.id] = partner.id
            else:
                # Two partners with the same receivable account: ignore
                # this account!
                accounts_map[partner.property_account_payable.id] = 0
        return accounts_map


    def action_import(self, cr, uid, ids, context=None):
        """
        Imports a CSV file into a new account move using the options from
        the wizard.
        """
        accounts_map = self._get_accounts_map(cr, uid, context=context)
        field_obj = self.pool.get('ir.model.fields')
        partner_obj = self.pool.get('res.partner')
        reFloat = r'(^[+-]?\d+(?:\.\d+)?(?:[eE][+-]\d+)?$)'

        for wiz in self.browse(cr, uid, ids, context=context):
            if not wiz.input_file:
                raise osv.except_osv(_('UserError'), _("You need to select a file!"))

            account_move_data = self.pool.get('account.move').default_get(cr, uid, ['state', 'name'])
            account_move_data.update({
                    'ref': wiz.ref,
                    'journal_id': wiz.journal_id.id,
                    'period_id': wiz.period_id.id,
                    'date': wiz.date,
                    'type': wiz.type,
                    'line_id': [],
                    'partner_id': False,
                    'to_check': 0
                })

            lines_data = account_move_data['line_id']

            # Decode the file data
            data = base64.b64decode(wiz.input_file)

            #
            # Read the file
            #
            reader = csv.reader(StringIO.StringIO(data),
                                delimiter=str(wiz.csv_delimiter),
                                quotechar=str(wiz.csv_quotechar))

            for record in reader:
                # Ignore short records
                if wiz.csv_partner_ref_index and len(record) > wiz.csv_code_index \
                        and len(record) > wiz.csv_ref_index \
                        and len(record) > wiz.csv_debit_index \
                        and len(record) > wiz.csv_credit_index:

                    record_code = record[wiz.csv_code_index]
                    record_ref = record[wiz.csv_ref_index]
                    record_debit = record[wiz.csv_debit_index]
                    record_credit = record[wiz.csv_credit_index]
                    record_partner_ref = False

                    if len(record) > wiz.csv_partner_ref_index:
                        record_partner_ref = record[wiz.csv_partner_ref_index]

                    #
                    # Ignore invalid records
                    #
                    if re.match(wiz.csv_code_regexp, record_code) \
                            and re.match(wiz.csv_ref_regexp, record_ref) \
                            and re.match(wiz.csv_debit_regexp, record_debit) \
                            and re.match(wiz.csv_credit_regexp, record_credit):

                        #
                        # Clean the input amounts or fail
                        #
                        if record_debit:
                            record_debit = record_debit.replace(
                                        wiz.csv_thousands_separator, '').\
                                    replace(
                                        wiz.csv_decimal_separator, '.')
                            if re.match(reFloat, record_debit):
                                record_debit = float(record_debit)
                            else:
                                raise osv.except_osv(_('Error'),
                                    _("The debit quantity %s doesn't match with"\
                                      " a regex float value in account %s") %
                                    (record_debit, record_code))
                        else:
                            record_debit = 0.0
                        if record_credit:
                            record_credit = record_credit.replace(
                                        wiz.csv_thousands_separator, '').\
                                    replace(
                                        wiz.csv_decimal_separator, '.')
                            if re.match(reFloat, record_credit):
                                record_credit = float(record_credit)
                            else:
                                raise osv.except_osv(_('Error'),
                                    _("The credit quantity %s doesn't match with"\
                                      " a regex float value in account %s") %
                                    (record_credit, record_code))
                        else:
                            record_credit = 0.0

                        #
                        # Find the account (or fail!)
                        #
                        account_ids = self.pool.get('account.account').search(cr, uid, [
                                    ('code', '=', record_code),
                                    ('company_id', '=', wiz.company_id.id)
                                ])
                        if not account_ids:
                            raise osv.except_osv(_('Error'), _("Account not found: %s!") % record_code)

                        #
                        # Find the partner searching in the oerp_partner_ref_field
                        #
                        partner_id = False
                        if record_partner_ref and re.match(
                                wiz.csv_partner_ref_regexp,
                                record_partner_ref):
                            field = field_obj.browse(cr, uid,
                                    wiz.oerp_partner_ref_field.id, context).name
                            partner_ids = partner_obj.search(cr, uid,
                                    [(field, '=', record_partner_ref)])
                            if partner_ids:
                                partner_id = partner_ids[0]

                        #
                        # Prepare the line data
                        #
                        line_data = {
                            'account_id': account_ids[0],
                            'debit': 0.0,
                            'credit': 0.0,
                            'name': record_ref,
                            'ref': False,
                            'currency_id': False,
                            'tax_amount': False,
                            'partner_id': partner_id or (accounts_map.get(account_ids[0]) or False),
                            'tax_code_id': False,
                            'date_maturity': False,
                            'amount_currency': False,
                            'analytic_account_id': False,
                        }

                        #
                        # Create a debit line + a credit line if needed
                        #
                        line_data_debit = line_data.copy()
                        line_data_credit = line_data
                        if record_debit != 0.0:
                            line_data_debit['debit'] = record_debit
                            lines_data.append((0, 0, line_data_debit))
                        if record_credit != 0.0:
                            line_data_credit['credit'] = record_credit
                            lines_data.append((0, 0, line_data_credit))
                    else:
                        netsvc.Logger().notifyChannel('account_move_importer', netsvc.LOG_WARNING,
                                "Invalid record format (ignoring line): %s" % repr(record))
                else:
                    netsvc.Logger().notifyChannel('account_move_importer', netsvc.LOG_WARNING,
                            "Too short record (ignoring line): %s" % repr(record))


        # Finally create the move
        move_id = self.pool.get('account.move').create(cr, uid, account_move_data)

        #
        # Show the move to the user
        #
        model_data_ids = self.pool.get('ir.model.data').search(cr, uid, [
                    ('model', '=', 'ir.ui.view'),
                    ('module', '=', 'account'),
                    ('name', '=', 'view_move_form')
                ])
        resource_id = self.pool.get('ir.model.data').read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

        return {
            'name': _("Imported account moves"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form,tree',
            #'view_id': (resource_id, 'View'),
            'views': [(False, 'tree'), (resource_id, 'form')],
            'domain': "[('id', '=', %s)]" % move_id,
            'context': context,
        }




pxgo_account_move_importer()


