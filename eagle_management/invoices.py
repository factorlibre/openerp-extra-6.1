# -*- coding: utf-8 -*-
#
#  File: invoices.py
#  Module: eagle_contracts
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
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
	
	def create(self, cr, uid, vals, context=None):
		do_it = False
		if 'contract_id' not in vals:
			do_it = True
		if not do_it:
			if not vals['contract_id']:
				do_it = True
		contract_id = False
		if do_it and 'invoice_line' in vals and vals['invoice_line']:
			inv_lines = vals['invoice_line']
			if inv_lines and inv_lines[0] and inv_lines[0][2] and len(inv_lines[0][2]) > 0:
				if isinstance(inv_lines[0][2],list):
					cr.execute( """select sol.contract_id
from sale_order_line_invoice_rel rel, sale_order_line sol
where rel.order_line_id=sol.id
and rel.invoice_id = %d""" % inv_lines[0][2][0] )
					row = cr.fetchone()
					if row and len(row) > 0:
						contract_id = row[0]
		
		# If the contract ID wasn't found, let's try with the invoice's origin
		if do_it and not contract_id:
			if 'origin' in vals and vals['origin']:
				cr.execute("Select contract_id from sale_order Where name='%s'" % vals['origin'] )
				row = cr.fetchone()
				if row and len(row) > 0:
					contract_id = row[0]

		if contract_id:
			vals['contract_id'] = contract_id

		return super( account_invoice, self ).create(cr, uid, vals, context)

account_invoice()
