# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP s.a (<http://www.openerp.com).
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

from osv import osv

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_number(self, cr, uid, ids, context=None):
        res = super(account_invoice,self).action_number(cr, uid, ids, context) 
        claim_obj = self.pool.get('crm.claim')
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type in ['in_refund', 'out_refund']:
                vals = {
                       'name': invoice.name or invoice.number,
                       'date': invoice.date_invoice, 
                       'ref' : 'account.invoice,' + str(invoice.id), 
                       'planned_revenue': invoice.type == 'in_refund' and invoice.amount_total or 0.0, 
                       'planned_cost': invoice.type == 'out_refund' and invoice.amount_total or 0.0, 
                       'type_action': 'correction',
                       'company_id': invoice.company_id.id,
                       'partner_id': invoice.partner_id.id,
                       'partner_address_id': invoice.address_contact_id.id,
                   }
                vals.update(claim_obj.onchange_partner_id(cr, uid, ids, invoice.partner_id.id)['value'])
                vals.update(claim_obj.onchange_partner_address_id(cr, uid, ids, invoice.address_contact_id.id)['value'])
                claim_obj.create(cr, uid, vals, context)

        return res 


account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
