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

import netsvc
import pooler
import time
from report import report_sxw

class report_labo_request(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(report_labo_request, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'get_description': self.get_description,
			'get_title':self.get_title,

		})

	def get_description(self,object):
		attach_ids = self.pool.get('ir.attachment').search(self.cr, self.uid, [('res_model','=','labo.analysis.request'), ('res_id', '=',object.id)])
		datas = self.pool.get('ir.attachment').read(self.cr, self.uid, attach_ids)
		if len(datas):
			return datas[0]['datas_fname']
		return ""

	def get_title(self,object):
		if object.type_id.code =='EMPBOV':
			return "EMPREINTES BOVINES"
		elif  object.type_id.code =='Scrapie':
			return "SCRAPIE"
		elif object.type_id.code =='Id of race':
			return "STRESS"# TO CONFIRM
		elif object.type_id.code =='Sequence':
			return "SEQUENCE"
		return object.type_id.code


report_sxw.report_sxw('report.labo_analysis_request', 'labo.analysis.request', 'addons/labo_analysis/report/labo_request.rml',parser=report_labo_request)
