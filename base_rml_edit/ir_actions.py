# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields
import binascii
import netsvc

class report_xml(osv.osv):
    
    def _report_content_txt(self, cr, uid, ids, name, arg, context=None):
	if context is None: context = {}
        res = {}
	context['bin_size'] = False
        for report in self.read(cr,uid,ids,['report_rml_content'],context=context):
            data = report['report_rml_content']
            res[report['id']] = data
        return res

    def _report_content_txt_inv(self, cr, uid, id, name, value, arg, context=None):
	self.write(cr,uid,id,{'report_rml_content':str(value)},context=context)
    
    
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'
    _columns = {
	    'report_rml_content_txt': fields.function(_report_content_txt, fnct_inv=_report_content_txt_inv, method=True, type='text', string='RML text content'),
	    
	}
	
    
report_xml()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
