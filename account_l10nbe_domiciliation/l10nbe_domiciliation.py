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

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _description = 'Account Invoice'
    _columns = {
        'domiciled' : fields.boolean('Domiciled'),
        'domiciled_send_date' : fields.date('Domiciliation Sending Date', readonly=True, help='This field contains the sending date of the document for direct debit invoices collecting'),
        }

    def on_change_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False):
        data=super(account_invoice,self).onchange_partner_id( cr, uid, ids, type, partner_id,date_invoice, payment_term)
        if not partner_id:
            return data['value'].update({'domiciled' : False})
        partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
        domiciled = partner_obj.domiciliation_bool
        data['value']['domiciled'] = domiciled
        return data

account_invoice()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'Partner'
    _columns = {
        'domiciliation_bool':fields.boolean('Direct Debit Permission', help="Check this field if you can collect direct debit invoices for this partner."),
        'domiciliation' : fields.char('Direct Debit Number', size=12)
        }
res_partner()

class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
        'institution_code':fields.char('Institution Code', size=3, help="Code of the financial institution used for Dom80 Export"),
    }
res_partner_bank()

class invoice_export_log(osv.osv):
    _name = "invoice.export.log"
    _description = "Invoice Export History"
    _rec_name = 'invoice_id'
    _columns = {
        'state': fields.selection([('failed', 'Failed'), ('succeeded', 'Succeeded')], 'Status', readonly=True),
        'file': fields.binary('Saved File', readonly=True),
        'note': fields.text('Creation Log', readonly=True),
        'create_date': fields.datetime('Creation Date', required=True, readonly=True),
        'create_uid': fields.many2one('res.users', 'Creation User', required=True, readonly=True),
    }
invoice_export_log()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

