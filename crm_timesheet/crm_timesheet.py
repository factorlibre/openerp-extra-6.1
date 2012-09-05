# -*- coding: utf-8 -*-
##############################################################################
#
#    crm_timesheet module for openerp, CRM timesheet
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    copyright (c) 2011 syleam info services (<http://www.syleam.fr/>) 
#              sebastien lange <sebastien.lange@syleam.fr>
#
#    this file is a part of crm_timesheet
#
#    crm_timesheet is free software: you can redistribute it and/or modify
#    it under the terms of the gnu general public license as published by
#    the free software foundation, either version 3 of the license, or
#    (at your option) any later version.
#
#    crm_timesheet is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _
from tools import ustr
import time


class crm_analytic_timesheet(osv.osv):
    _name = 'crm.analytic.timesheet'
    _description = 'CRM summary work'

    _columns = {
        'name': fields.char('Work summary', size=128),
        'model': fields.char('Object Name', size=128, select=1, readonly=True),
        'res_id': fields.integer('Resource ID', select=1, readonly=True),
        'date': fields.datetime('Date'),
        'hours': fields.float('Time spent'),
        'user_id': fields.many2one('res.users', 'Done by', required=True),
        'hr_analytic_timesheet_id':fields.many2one('hr.analytic.timesheet','Related Timeline Id', ondelete='set null'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete='cascade', required=True,),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _order = "date desc"

    def get_user_related_details(self, cr, uid, user_id):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', user_id)])
        if not emp_id:
            user_name = self.pool.get('res.users').read(cr, uid, [user_id], ['name'])[0]['name']
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No employee defined for user "%s". You must create one.')% (user_name,))
        emp = self.pool.get('hr.employee').browse(cr, uid, emp_id[0])
        if not emp.product_id:
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No product defined on the related employee.\nFill in the timesheet tab of the employee form.'))

        if not emp.journal_id:
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No journal defined on the related employee.\nFill in the timesheet tab of the employee form.'))

        a = emp.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = emp.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Bad Configuration !'),
                        _('No product and product category property account defined on the related employee.\nFill in the timesheet tab of the employee form.'))
        res['product_id'] = emp.product_id.id
        res['journal_id'] = emp.journal_id.id
        res['general_account_id'] = a
        res['product_uom_id'] = emp.product_id.uom_id.id
        return res

    def create(self, cr, uid, values, context=None):
        """
        #TODO make doc string
        Comment this
        """
        if context is None:
            context = {}
        if context.get('model', False):
            obj_timesheet = self.pool.get('hr.analytic.timesheet')
            case_obj = self.pool.get(context['model'])
            uom_obj = self.pool.get('product.uom')

            values_line = {}
            obj_case = case_obj.browse(cr, uid, values['res_id'])
            result = self.get_user_related_details(cr, uid, values.get('user_id', uid))
            values_line['name'] = '%s: %s' % (ustr(obj_case.name), ustr(values['name']) or '/')
            values_line['user_id'] = values['user_id']
            values_line['product_id'] = result['product_id']
            values_line['date'] = values['date'][:10]

            #calculate quantity based on employee's product's uom 
            values_line['unit_amount'] = values['hours']

            default_uom = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id.id
            if result['product_uom_id'] != default_uom:
                values_line['unit_amount'] = uom_obj._compute_qty(cr, uid, default_uom, values['hours'], result['product_uom_id'])
            acc_id = values_line['account_id'] = values['analytic_account_id']
            res = obj_timesheet.on_change_account_id(cr, uid, False, acc_id)
            if res.get('value'):
                values_line.update(res['value'])
            values_line['general_account_id'] = result['general_account_id']
            values_line['journal_id'] = result['journal_id']
            values_line['amount'] = 0.0
            values_line['product_uom_id'] = result['product_uom_id']
            amount = values_line['unit_amount']
            prod_id = values_line['product_id']
            unit = False
            timeline_id = obj_timesheet.create(cr, uid, values_line, context=context)

            # Compute based on pricetype
            amount_unit = obj_timesheet.on_change_unit_amount(cr, uid, timeline_id,
                prod_id, amount, False, unit, values_line['journal_id'], context=context)
            if amount_unit and 'amount' in amount_unit.get('value',{}):
                updv = { 'amount': amount_unit['value']['amount'] }
                obj_timesheet.write(cr, uid, [timeline_id], updv, context=context)
            values['hr_analytic_timesheet_id'] = timeline_id
            values['model'] = context['model']
        return super(crm_analytic_timesheet, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if context.get('model', False):
            timesheet_obj = self.pool.get('hr.analytic.timesheet')
            crm_obj = self.pool.get(context['model'])
            uom_obj = self.pool.get('product.uom')
            result = {}

            if isinstance(ids, (long, int)):
                ids = [ids,]

            for timesheet in self.browse(cr, uid, ids, context=context):
                line_id = timesheet.hr_analytic_timesheet_id
                if not line_id:
                    # if a record is deleted from timesheet, the line_id will become
                    # null because of the foreign key on-delete=set null
                    continue
                vals_line = {}
                if 'name' in vals:
                    vals_line['name'] = '%s: %s' % (ustr(crm_obj.browse(cr, uid, timesheet.res_id, context=context).name), ustr(vals['name']) or '/')
                if 'user_id' in vals:
                    vals_line['user_id'] = vals['user_id']
                    result = self.get_user_related_details(cr, uid, vals['user_id'])
                    for fld in ('product_id', 'general_account_id', 'journal_id', 'product_uom_id'):
                        if result.get(fld, False):
                            vals_line[fld] = result[fld]

                if 'date' in vals:
                    vals_line['date'] = vals['date'][:10]
                if 'hours' in vals:
                    default_uom = self.pool.get('res.users').browse(cr, uid, uid).company_id.crm_time_mode_id.id
                    vals_line['unit_amount'] = vals['hours']
                    prod_id = vals_line.get('product_id', line_id.product_id.id) # False may be set

                    if result.get('product_uom_id',False) and (not result['product_uom_id'] == default_uom):
                        vals_line['unit_amount'] = uom_obj._compute_qty(cr, uid, default_uom, vals['hours'], result['product_uom_id'])

                    # Compute based on pricetype
                    amount_unit = timesheet_obj.on_change_unit_amount(cr, uid, line_id.id,
                        prod_id=prod_id, company_id=False,
                        unit_amount=vals_line['unit_amount'], unit=False, journal_id=vals_line['journal_id'], context=context)

                    if amount_unit and 'amount' in amount_unit.get('value',{}):
                        vals_line['amount'] = amount_unit['value']['amount']

                self.pool.get('hr.analytic.timesheet').write(cr, uid, [line_id.id], vals_line, context=context)

        return super(crm_analytic_timesheet,self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, *args, **kwargs):
        hat_obj = self.pool.get('hr.analytic.timesheet')
        hat_ids = []
        for timesheet in self.browse(cr, uid, ids):
            if timesheet.hr_analytic_timesheet_id:
                hat_ids.append(timesheet.hr_analytic_timesheet_id.id)
        # delete entry from timesheet too while deleting entry to task.
        if hat_ids:
            hat_obj.unlink(cr, uid, hat_ids, *args, **kwargs)
        return super(crm_analytic_timesheet,self).unlink(cr, uid, ids, *args, **kwargs)

crm_analytic_timesheet()

class crm_analytic_timesheet_configuration(osv.osv):
    _name = 'crm.analytic.timesheet.configuration'
    _description = 'Add value by default in CRM'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help="Name of this parameter, use in partner",),
        'model': fields.char('Model', size=128, required=True, help="Model of OpenERP, eg: crm.lead",),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete='cascade', required=True, help="Analytic account by default for the model indicated",),
    }

    _sql_constraints = [
        ('model_uniq', 'unique (model)', 'The model of the OpenERP must be unique !'),
    ]

crm_analytic_timesheet_configuration()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
