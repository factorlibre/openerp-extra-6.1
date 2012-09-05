# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenOffice Reports
#    Copyright (C) 2009 Pexego Sistemas Informáticos. All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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
##############################################################################

"""
Extends report_xml to add new report types to the report_type selection.
"""
__author__ = "Borja López Soilán (Pexego)"

import os
import base64
from osv import osv, fields
import openoffice_report
from tools.translate import _

class report_xml_file(osv.osv):
    _name = 'ir.actions.report.xml.file'
    _columns = {
        'file': fields.binary('File', required=True, filters="*.odt,*.pdf,*.html,*.doc,*.rtf,*.txt,*.ods,*.xls,*.csv,*.odp,*.ppt,*.swf", help=''),
        'filename': fields.char('File Name', size=256, required=False, help=''),
        'report_id': fields.many2one('ir.actions.report.xml', 'Report', required=True, ondelete='cascade', help=''),
        'default': fields.boolean('Default', help=''),
    }
    def create(self, cr, uid, vals, context=None):
        result = super(report_xml_file,self).create(cr, uid, vals, context)
        self.pool.get('ir.actions.report.xml').update(cr, uid, [vals['report_id']], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(report_xml_file,self).write(cr, uid, ids, vals, context)
        for attachment in self.browse(cr, uid, ids, context):
            self.pool.get('ir.actions.report.xml').update(cr, uid, [attachment.report_id.id], context)
        return result

report_xml_file()

class report_xml(osv.osv):
    """
    Extends report_xml to add new report types to the report_type selection.

    You may declare reports of the new types like this
        <report id="report_REPORTNAME"
            ... />
        <record model="ir.actions.report.xml" id="report_REPORTNAME">
            <field name="report_type">oo-odt</field>
        </record>
    """
    
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'report_type': fields.selection([
                ('pdf', 'pdf'),
                ('html', 'html'),
                ('raw', 'raw'),
                ('sxw', 'sxw'),
                ('odt', 'odt'),
                ('html2html','Html from html'),
                ('oo-pdf', 'OpenOffice - pdf output'),
                ('oo-html', 'OpenOffice - html output'),
                ('oo-odt', 'OpenOffice - odt output'),
                ('oo-doc', 'OpenOffice - doc output'),
                ('oo-rtf', 'OpenOffice - rtf output'),
                ('oo-txt', 'OpenOffice - txt output'),
                ('oo-ods', 'OpenOffice - ods output'),
                ('oo-xls', 'OpenOffice - xls output'),
                ('oo-csv', 'OpenOffice - csv output'),
                ('oo-odp', 'OpenOffice - odp output'),
                ('oo-ppt', 'OpenOffice - ppt output'),
                ('oo-swf', 'OpenOffice - swf output'),
            ], string='Type', required=True),
        'openoffice_file_ids': fields.one2many('ir.actions.report.xml.file', 'report_id', 'Files', help=''),
        'openoffice_model_id': fields.many2one('ir.model', 'Model', help=''),
        'openoffice_report': fields.boolean('Is OpenOffice Report?', help=''),
    }

    def create(self, cr, uid, vals, context=None):
        if context and context.get('openoffice_report'):
            vals['model'] = self.pool.get('ir.model').browse(cr, uid, vals['openoffice_model_id'], context).model
            vals['type'] = 'ir.actions.report.xml'
#            vals['report_type'] = 'pdf'
            vals['openoffice_report'] = True
            vals['header'] = False

        return super(report_xml, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context and context.get('openoffice_report'):
            if 'openoffice_model_id' in vals:
                vals['model'] = self.pool.get('ir.model').browse(cr, uid, vals['openoffice_model_id'], context).model
            vals['type'] = 'ir.actions.report.xml'
#            vals['report_type'] = 'pdf'
            vals['openoffice_report'] = True
            vals['header'] = False

        return super(report_xml, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """Deletes ir_values register when you delete any ir.actions.report.xml"""
        if context is None: context = {}
        for report in self.browse(cr, uid, ids):
            values = self.pool.get('ir.values').search(cr, uid, [('value','=','ir.actions.report.xml,%s'% report.id)])
            if values:
                self.pool.get('ir.values').unlink(cr, uid, values)

        return super(report_xml, self).unlink(cr, uid, ids, context=context)

    def update(self, cr, uid, ids, context={}):
        """Browse attachments and store .odt into pxgo_openoffixe_reprots/custom_reports
        directory. Also add or update ir.values data so they're shown on model views."""
        for report in self.browse(cr, uid, ids):
            has_default = False

            for attachment in report.openoffice_file_ids:
                content = attachment.file
                fileName = attachment.filename

                if not fileName or not content:
                    continue

                path = self.save_file( fileName, content )
                for extension in ['.odt','.pdf','.html','.doc','.rtf','.txt','.ods','.xls','.csv','.odp','.ppt','.swf']:
                    if extension in fileName:
                        if attachment.default:
                            if has_default:
                                raise osv.except_osv(_('Error'), _('There is more than one report marked as default'))

                            has_default = True
                            # Update path into report_rml field.
                            self.write(cr, uid, [report.id], {
                                'report_rml': path
                            })

                            valuesId = self.pool.get('ir.values').search(cr, uid, [('value','=','ir.actions.report.xml,%s'% report.id)])
                            data = {
                                'name': report.name,
                                'model': report.model,
                                'key': 'action',
                                'object': True,
                                'key2': 'client_print_multi',
                                'value': 'ir.actions.report.xml,%s'% report.id
                            }
                            
                            if not valuesId:
                                valuesId = self.pool.get('ir.values').create(cr, uid, data, context=context)
                            else:
                                self.pool.get('ir.values').write(cr, uid, valuesId, data, context=context)
                                valuesId = valuesId[0]

            if not has_default:
                raise osv.except_osv(_('Error'), _('No report has been marked as default.'))

            # Ensure the report is registered so it can be used immediately
            openoffice_report.openoffice_report( report.report_name, report.model )
            
        return True

    def save_file(self, name, value):
        """save the file to pxgo_openoffice_reports/custom_reports"""
        path = os.path.abspath( os.path.dirname(__file__) )
        path += '/custom_reports/%s' % name
        f = open( path, 'wb+' )
        try:
            f.write( base64.decodestring( value ) )
        finally:
            f.close()
        path = 'pxgo_openoffice_reports/custom_reports/%s' % name
        return path

report_xml()
