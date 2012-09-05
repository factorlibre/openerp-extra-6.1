# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import osv, fields

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _description = "Picking List"

    _columns = {
                'fiscal_position': fields.many2one('account.fiscal.position', 'Posição Fiscal', domain="[('fiscal_operation_id','=',fiscal_operation_id)]"),
                }

    def onchange_partner_in(self, cr, uid, context=None, partner_id=None,company_id=False):

        result = super(stock_picking, self).onchange_partner_in(cr, uid, context, partner_id)

        if not company_id or not partner_id:
            return result
        
        if not result:
            result = {'value': {'fiscal_position_id': False}}
        
        partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, partner_id)
        
        to_country = partner_addr_default.country_id.id
        to_state = partner_addr_default.state_id.id

        if partner_addr_default.partner_id.id:
            obj_partner = self.pool.get('res.partner').browse(cr, uid, partner_addr_default.partner_id.id)
    
            if obj_partner.property_account_position:
                result['value']['fiscal_position'] = obj_partner.property_account_position.id
                return result

        obj_company = self.pool.get('res.company').browse(cr, uid, company_id)

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, ['&',('company_id','=', company_id),('use_picking','=',True),'|' , ('from_country','=',from_country),('from_country','=',False),'|' ,('to_country','=',to_country),('to_country','=',False),'|',('from_state','=',from_state),('from_state','=',False),'|',('to_state','=',to_state),('to_state','=',False)])
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').read(cr, uid, fsc_pos_id, ['fiscal_position_id'])
            result['value']['fiscal_position'] = obj_fpo_rule[0]['fiscal_position_id']

        return result
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        result = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
        
        if not result:
            return result
        
        obj_invoice = self.pool.get('account.invoice')
        
        for picking_id in result.keys():
            
            invoice_id = result[picking_id]
            
            for picking in self.browse(cr, uid, [picking_id], context=context):
            
                fiscal_position = picking.partner_id.property_account_position or (picking.sale_id and picking.sale_id.fiscal_position) or picking.fiscal_position
                
                if fiscal_position:
                    obj_invoice.write(cr, uid, invoice_id, {
                                                             'fiscal_position': fiscal_position.id, 
                                                             })
                    
                    for invoice in obj_invoice.browse(cr, uid, [invoice_id], context=context):
                        
                        for invoice_line in invoice.invoice_line:
                        
                            if invoice.type in ('in_invoice', 'in_refund'):
                                taxes = invoice_line.product_id.supplier_taxes_id
                            else:
                                taxes = invoice_line.product_id.taxes_id
        
                            map_tax = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, taxes)
                            
                            self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {
                                                                     'invoice_line_tax_id': [(6, 0, map_tax)], 
                                                                     })
                            
                    obj_invoice.button_compute(cr, uid, [invoice.id], context=context,
                    set_total=(invoice.type in ('in_invoice', 'in_refund')))
                    
        return result

stock_picking()
