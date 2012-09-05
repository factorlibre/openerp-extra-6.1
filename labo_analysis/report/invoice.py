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

import time
from report import report_sxw

class account_invoice(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(account_invoice, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'_get_tax_notes':self._get_tax_notes,
		})

	def _get_tax_notes(self, o):
		note_uniq=[]
		notes=''
		text_notes=[]
		for a in o.invoice_line:
			for i in a.invoice_line_tax_id:
				text_notes.append(i.note or '')
		note_uniq=dict([i,0] for i in text_notes)
		notes=",".join([str(x) for x in note_uniq if x])
		return notes
		return ''


report_sxw.report_sxw('report.labo_analysis.invoice', 'account.invoice', 'addons/labo_analysis/report/invoice.rml', parser=account_invoice)

