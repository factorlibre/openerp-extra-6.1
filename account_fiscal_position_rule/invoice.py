# -*- encoding: utf-8 -*-
#################################################################################
#
#    Copyright (C) 2010  Renato Lima - Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
#################################################################################

from osv import fields, osv

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):

        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)

        if not partner_id or not company_id or not result['value']['address_invoice_id'] or result['value']['fiscal_position']:
            return result

        obj_company = self.pool.get('res.company').browse(cr, uid, company_id)

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [result['value']['address_invoice_id']])[0]

        to_country = partner_addr_default.country_id.id
        to_state = partner_addr_default.state_id.id

        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, ['&',('use_invoice','=',True), ('company_id','=',company_id), '|',('from_country','=',from_country), ('from_country','=',False), '|', ('to_country','=',to_country),('to_country','=',False),'|',('from_state','=',from_state),('from_state','=',False),'|',('to_state','=',to_state),('to_state','=',False)])
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').read(cr, uid, fsc_pos_id,['fiscal_position_id'])
            result['value']['fiscal_position'] = obj_fpo_rule[0]['fiscal_position_id']

        return result
                            
    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id, ptn_invoice_id):
         
        result = super(account_invoice, self).onchange_company_id(cr, uid, ids, company_id, part_id, type, invoice_line, currency_id)
        
        if not part_id or not company_id or not ptn_invoice_id:
            return result
        
        obj_partner = self.pool.get('res.partner').browse(cr, uid, part_id)
        if obj_partner.property_account_position:
            result['value']['fiscal_position'] = obj_partner.property_account_position.id
            return result
        
        obj_company = self.pool.get('res.company').browse(cr, uid, company_id)
        
        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]
        
        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id])[0]

        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id

        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, ['&',('company_id','=', company_id),('from_country','=',from_country),('to_country','=',to_country),('use_invoice','=',True),'|',('from_state','=',from_state),('from_state','=',False),'|',('to_state','=',to_state),('to_state','=',False)])
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').read(cr, uid, fsc_pos_id, ['fiscal_position_id'])
            result['value']['fiscal_position'] = obj_fpo_rule[0]['fiscal_position_id']
       
        return result   
    
    def onchange_address_invoice_id(self, cr, uid, ids, cpy_id, ptn_id, ptn_invoice_id):

        result = {'value': {'fiscal_position': False}}
        
        if not ptn_id or not cpy_id or not ptn_invoice_id or result['value']['fiscal_position']:
            return result

        obj_partner = self.pool.get('res.partner').browse(cr, uid, ptn_id)
        if obj_partner.property_account_position:
            result['value']['fiscal_position'] = obj_partner.property_account_position.id
            return result

        obj_company = self.pool.get('res.company').browse(cr, uid, cpy_id)
        
        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]
        
        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, ptn_invoice_id)

        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id

        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, ['&',('use_invoice','=',True), ('company_id','=', cpy_id), '|',('from_country','=',from_country), ('from_country','=', False), '|', ('to_country','=',to_country), ('to_country','=',False), '|',('from_state','=',from_state),('from_state','=',False),'|',('to_state','=',to_state),('to_state','=',False)])
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').read(cr, uid, fsc_pos_id,['fiscal_position_id'])
            result['value']['fiscal_position'] = obj_fpo_rule[0]['fiscal_position_id']

        return result

account_invoice()
