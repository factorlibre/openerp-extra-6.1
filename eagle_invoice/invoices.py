# -*- coding: utf-8 -*-
#
#  File: invoices.py
#  Module: eagle_invoice
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import netsvc
from osv import fields, osv

class account_invoice( osv.osv ):
	_inherit = 'account.invoice'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'financial_partner_id': fields.many2one( 'res.partner', 'Financial partner' ),
	}

	def write(self, cr, uid, ids, vals, context=None):
		ret = super( account_invoice, self).write( cr, uid, ids, vals, context=context )
		if 'contract_id' in vals:
			if isinstance(ids, (int, long)):
				ids = [ids]
			for invoice in self.browse( cr, uid, ids, context=context ):
				for inv_l in invoice.invoice_line:
					self.pool.get( 'account.invoice.line' ).write( cr, uid, inv_l.id, {'contract_id':vals['contract_id']}, context=context )
		
		return ret

account_invoice()

class account_invoice_line( osv.osv ):
	_inherit = 'account.invoice.line'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'contract_position_id': fields.many2one( 'eagle.contract.position', 'Contract Position' ),
	}
	
	def create(self, cr, uid, vals, context=None):
		if 'contract_id' not in vals:
			if 'invoice_id' in vals and vals['invoice_id']:
				inv = self.pool.get( 'account.invoice' ).browse( cr, uid, vals['invoice_id'], context=context )
				if inv: vals['contract_id'] = inv.contract_id
		
		return super( account_invoice_line, self).create( cr, uid, vals, context=context )

	def write(self, cr, uid, ids, vals, context=None):
		if 'contract_id' not in vals:
			for invl in self.browse( cr, uid, ids, context=context ):
				if invl.invoice_id: 
					vals['contract_id'] = invl.invoice_id.contract_id and invl.invoice_id.contract_id.id or False
					break

		return super( account_invoice_line, self).write( cr, uid, ids, vals, context=context )

account_invoice_line()
