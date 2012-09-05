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

class report_scid(report_sxw.rml_parse):

	 def __init__(self, cr, uid, name, context):
		super(report_scid, self).__init__(cr, uid, name, context)
		self.localcontext.update({
				'time': time,
				'get_sample':self.get_sample
		  })

	 def get_sample(self,request):
		print "request obje",request.id
		self.cr.execute('select count(id) from labo_sample where sample_id=%d'%(request.id,))
		res = self.cr.fetchone()
		return str(res[0] or 0)

report_sxw.report_sxw('report.List_scid', 'labo.analysis.request', 'addons/labo_analysis/report/report_scid_2007_0276.rml',parser=report_scid)


