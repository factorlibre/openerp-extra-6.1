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
from osv import fields, osv
import time
import pickle
from tools.translate import _

class account_move(osv.osv):
    _inherit = "account.move"
    _description = "Account Entry"

    def write(self, cr, uid, ids, vals, context=None):
        line_ids = []
        if vals.get('period_id', False):
            lines = self.browse(cr, uid, ids, context=context)[0].line_id
            map(lambda x: line_ids.append(x.id),lines)
            self.pool.get('account.move.line').write(cr, uid, line_ids, {'period_id': vals['period_id']}, context=context)
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result

account_move()

class account_invoice(osv.osv):

    _inherit = "account.invoice"
    _order = "date_invoice desc"

    def _onchange_user_id(self, cr, uid, ids, user_id, status):
        result = {'value': {'user_id': user_id}}
        data_pool = self.pool.get('ir.model.data')
        user_obj =  self.pool.get('res.users')
        user_group_ids = user_obj.browse(cr, uid, uid).groups_id
        group_ch_user_id = data_pool._get_id(cr, uid, 'cci_account', 'group_inv_change_user')
        if group_ch_user_id:
            group_id = data_pool.browse(cr, uid, group_ch_user_id).res_id
        groups_user = [x.id for x in user_group_ids] 
        if (status not in ('open')) or ((status == 'open') and (group_id in groups_user)):
            result = {'value': {'user_id': user_id}}
        else:
            raise osv.except_osv('Error!','You don\'t have enough access to change the user on confirmed invoice.')
        return result
    
    _columns = {
        'name': fields.char('Description', size=64, select=True),
        'ref_move': fields.char('Ref Move', size=64, select=True),
        'dept':fields.many2one('hr.department','Department'),
        'invoice_special':fields.boolean('Special Invoice'),
        'internal_note': fields.text('Internal Note'),
        'vat_num' : fields.related('partner_id', 'vat',  type='char', string="VAT"),
        'create_uid': fields.many2one('res.users', 'Creation User', readonly=True),
        'user_id': fields.many2one('res.users', 'User'),
    }

    def create(self, cr, uid, vals, context={}):
        data_pool = self.pool.get('ir.model.data')
        user_obj =  self.pool.get('res.users')
        if context.get('type') == 'in_invoice' and not context.get('from_purchase'):
            user_group_ids = user_obj.browse(cr, uid, uid, context).groups_id
            group_inv_id = data_pool._get_id(cr, uid, 'cci_account','group_invoice_supplier')
            if group_inv_id:
                group_id = data_pool.browse(cr, uid, group_inv_id, context=context).res_id
                if group_id not in [x.id for x in user_group_ids]:
                    raise osv.except_osv('Error!','You don\'t have enough access to create a supplier invoice.')
        if vals.has_key('partner_id') and vals['partner_id']:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
            vals.update({'invoice_special':partner.invoice_special})
            values_obj = self.pool.get('ir.values')
            term_id = []
            term_ids = values_obj.search(cr, uid, [('key','=','default'),('name','=','payment_term'),('model','=','account.invoice'),('key2','=',vals['partner_id'])])
            if not term_ids:
                term_ids = self.pool.get('ir.values').search(cr, uid, [('key','=','default'),('name','=','payment_term'),('model','=','account.invoice')])
            if term_ids:
                vals.update({'payment_term':pickle.loads(str(values_obj.browse(cr, uid, term_ids)[0].value))})
        return super(account_invoice, self).create(cr, uid, vals, context=context)

    def action_move_create(self, cr, uid, ids, context=None):
        flag = membership_flag = False
        product_ids = []
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        data_invoice = self.browse(cr,uid,ids[0])
        #raise an error if one of the account_invoice_line doesn't have an analytic entry
        for line in data_invoice.invoice_line:
            if not line.analytics_id:
                flag = True
        if flag:
            raise osv.except_osv('Error!','Invoice line should have Analytic Distribution to create Analytic Entries.')
        super(account_invoice, self).action_move_create(cr, uid, ids, context)
        for invoice_rec in self.browse(cr, uid, ids): 
            if invoice_rec.move_id and not invoice_rec.ref_move:
                self.write(cr, uid, [invoice_rec.id], {'ref_move':invoice_rec.move_id.name})
        for lines in data_invoice.abstract_line_ids:
            if lines.product_id:
                product_ids.append(lines.product_id.id)
        if product_ids:
            data_product = self.pool.get('product.product').browse(cr,uid,product_ids)
            for product in data_product:
                if product.membership:
                    membership_flag = True
        if data_invoice.partner_id.alert_membership and membership_flag:
            raise osv.except_osv('Error!',data_invoice.partner_id.alert_explanation or 'Partner is not valid')
        #create other move lines if the invoice_line is related to a check payment or an AWEX credence
        for inv in self.browse(cr, uid, ids):
            for item in self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',inv.id)]):
                line = self.pool.get('account.invoice.line').browse(cr,uid, [item])[0]
                if line.cci_special_reference:
                    iml = []
                    if inv.type in ('in_invoice', 'in_refund'):
                        ref = inv.reference
                    else:
                        ref = self._convert_ref(cr, uid, inv.number)
                    temp = line.cci_special_reference.split('*')
                    obj = temp[0]
                    obj_id = int(temp[1])
                    obj_ref = self.pool.get(obj).browse(cr, uid, [obj_id])[0]
                    linename = False
                    if obj == "event.registration":
                        #acc_id = self.pool.get('account.account').search(cr, uid, [('name','=','Creances AWEX - Cheques Formations et Cheques Langues')])[0]
                        journal_id = self.pool.get('account.journal').search(cr, uid, [('name','=','CFL Journal')])[0]
                        amount = obj_ref.check_amount
                        linename = obj_ref.invoice_label
                    else:
                        journal_id = self.pool.get('account.journal').search(cr, uid, [('name','=','AWEX Journal')])[0]
                        #acc_id = self.pool.get('account.account').search(cr, uid, [('name','=','Creances AWEX - Cheques Formations et Cheques Langues')])[0]
                        amount = obj_ref.awex_amount
                        linename = obj_ref.order_desc
                    acc_id = self.pool.get('account.journal').browse(cr, uid, [journal_id])[0].default_debit_account_id.id
                    iml.append({
                        'type': 'dest',
                        'name': linename or '/',
                        'price': amount,
                        'account_id': acc_id,
                        'date_maturity': inv.date_due or False,
                        'amount_currency': False,
                        'currency_id': inv.currency_id.id or False,
                        'ref': ref,
                    })
                    iml.append({
                        'type': 'dest',
                        'name': linename or '/',
                        'price': -(amount),
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due or False,
                        'amount_currency': False,
                        'currency_id': inv.currency_id.id or False,
                        'ref': ref,
                    })
                    date = inv.date_invoice
                    part = inv.partner_id.id
                    new_lines = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context={})) ,iml)
                    for item in new_lines:
                        if item[2]['credit']:
                            id1 = item[2]['credit']

                    journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
                    if inv.move_id:
                        name = inv.move_id.name
                    elif journal.sequence_id:
                        name = self.pool.get('ir.sequence').get_id(cr, uid, journal.sequence_id.id)
                    move = {'name': name, 'line_id': new_lines, 'journal_id': journal_id}
                    self.write(cr, uid, [inv.id], {'ref_move': inv.move_id.name})
                    if inv.period_id:
                        move['period_id'] = inv.period_id.id
                        #for i in line:
                        #    i[2]['period_id'] = inv.period_id.id
                    move_id = move_obj.create(cr, uid, move)
                    move_obj.post(cr, uid, [move_id])

                #this function could be improved in order to enable having more than one translation line per invoice
                    id1 = move_line_obj.search(cr, uid, [('move_id','=',move_id),('credit','<>',False)])[0]
                    id2 = move_line_obj.search(cr, uid, [('invoice','=',inv.id),('debit','<>',0)])[0]
                    move_line_obj.reconcile_partial(cr, uid, [id2,id1], 'manual', context=context)

        return True

    def action_number(self, cr, uid, ids, *args):
        res = super(account_invoice,self).action_number(cr, uid, ids, args)
        for inv in self.browse(cr, uid, ids):
            vcs =''
            if inv.number and not inv.name:
                vcs3 = inv.number.split('/')[1]
                vcs1 = '0'+ str(inv.date_invoice[2:4])
                if len(vcs3) >= 6:
                    vcs2= vcs3[0:6]
                else:
                    vcs2 = vcs3.rjust(6,'0')

                vcs4= vcs1 + vcs2 + '0'

                vcs5 = int(vcs4)
                check_digit = vcs5 % 97

                if check_digit == 0:
                    check_digit = '97'
                if check_digit <= 9:
                    check_digit = '0' + str(check_digit)
                vcs = vcs1 + '/' + vcs2[0:4] + '/' + vcs2[4:6] + '0' + str(check_digit)

                self.write(cr, uid, [inv.id], {'name':vcs})
                ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','=',inv.move_id.id)])
                self.pool.get('account.move').write(cr, uid, [inv.move_id.id], {'name' : inv.number})
        return res

    #raise an error if the partner has the warning 'alert_others' when we choose him in the account_invoice form
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False):
        warning = False
        inv_special=False
        domiciled = False
        user_id = False
        if partner_id:
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            domiciled = bool(data_partner.domiciliation)
            user_id = data_partner.user_id.id
            inv_special=data_partner.invoice_special
            if data_partner.alert_others:
                warning = {
                    'title': "Warning:",
                    'message': data_partner.alert_explanation or 'Partner is not valid'
                        }
        data=super(account_invoice,self).onchange_partner_id( cr, uid, ids, type, partner_id,date_invoice, payment_term)
        data['value']['domiciled'] = domiciled
        data['value']['user_id'] = user_id
        data['value']['invoice_special']=inv_special
        if warning:
            data['warning'] = warning
        return data

account_invoice()


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'dept' :  fields.many2one('hr.department','Department'),
    }

sale_order()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'cci_special_reference' : fields.char('Special Reference', size=64),
    }
    _defaults = {
        'cci_special_reference': lambda *a : False,
    }
account_invoice_line()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'
    def _check_st(self, cr, uid, ids):
        st_ids = self.search(cr, uid, [('state','=','draft')])
        if len(st_ids)>1:
            return False
        return True

  #  _constraints = [(_check_st, u"Can not open more that one statement", ('name',))]

account_bank_statement()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'

    def _check_account(self, cr, uid, ids):
        for line in self.browse(cr, uid, ids):
            if line.account_id.code in ('400000', '440000') and not line.partner_id:
                return False
        return True

    _constraints = [(_check_account, u"Can not register this line without partner", ('name',))]

account_bank_statement_line()

class account_move(osv.osv):
    _inherit = "account.move"
    def post(self, cr, uid, ids, context=None):
        move_ref = ''
        if context and context.get('invoice', None) and context['invoice']:
            move_ref = context['invoice'].number
        if self.validate(cr, uid, ids, context) and len(ids):
            for move in self.browse(cr, uid, ids):
                if move.name =='/':
                    new_name = False
                    journal = move.journal_id
                    if move_ref:
                        new_name = move_ref
                    elif journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        new_name = self.pool.get('ir.sequence').get_id(cr, uid, journal.sequence_id.id, context=c)
                    else:
                        raise osv.except_osv(_('Error'), _('No sequence defined in the journal !'))
                    if new_name:
                        self.write(cr, uid, [move.id], {'name':new_name})

            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s',
                       ('posted', tuple(ids)))
        else:
            raise osv.except_osv(_('Integrity Error !'), _('You can not validate a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        return True
account_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

