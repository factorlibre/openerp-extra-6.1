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
OpenOffice Reports - Reporting Engine based on Relatorio and OpenOffice.
"""
__author__ = "Borja López Soilán (Pexego)"

import os
import report
import pooler
import netsvc
import base64
import tempfile
import re
from tools.translate import _
from oo_template import OOTemplate, OOTemplateException
import mx.DateTime
from datetime import datetime
import time

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'


class OOReportException(Exception):
    """
    OpenERP report exception
    """
    def __init__(self, message):
        # pylint: disable-msg=W0231
        self.message = message
    def __str__(self):
        return self.message


class OOReport(object):
    """
    OpenOffice/Relatorio based report.
    """

    def log(self, message, level=netsvc.LOG_DEBUG):
        """
        Helper method used print debug messages
        """
        netsvc.Logger().notifyChannel('pxgo_openffice_reports', level, message)


    def __init__(self, name, cr, uid, ids, data, context):
        self.name = name
        self.cr = cr
        self.uid = uid
        self.ids = ids
        self.data = data
        self.model = self.data['model']
        self.context = context or {}
        self.dbname = cr.dbname
        self.pool = pooler.get_pool( cr.dbname )
        self.openoffice_port = 8100
        self.autostart_openoffice = True
        self.lang_dict_called = False
        self.lang_dict = {}
        self.default_lang = {}
        self._transl_regex = re.compile('(\[\[.+?\]\])')


    def get_report_context(self):
        """
        Returns the context for the report
        (Template method pattern)
        """
        return {}


    def _get_lang_dict(self):
        """
        Helper function that returns a function that
        sets the language for one object using the current database
        connection (cr) and user (uid).
        """
        pool_lang = self.pool.get('res.lang')
        lang = self.context.get('lang', False) or 'en_US'
        lang_ids = pool_lang.search(self.cr, self.uid, [('code','=',lang)])[0]
        lang_obj = pool_lang.browse(self.cr, self.uid, lang_ids)
        self.lang_dict.update({'lang_obj':lang_obj,'date_format':lang_obj.date_format,'time_format':lang_obj.time_format})
        self.default_lang[lang] = self.lang_dict.copy()
        return True

    def get_digits(self, obj=None, f=None, dp=None):
        """gets value for digits attribute"""
        d = DEFAULT_DIGITS = 2
        if dp:
            decimal_precision_obj = self.pool.get('decimal.precision')
            ids = decimal_precision_obj.search(self.cr, self.uid, [('name', '=', dp)])
            if ids:
                d = decimal_precision_obj.browse(self.cr, self.uid, ids)[0].digits
        elif obj and f:
            res_digits = getattr(obj._columns[f], 'digits', lambda x: ((16, DEFAULT_DIGITS)))
            if isinstance(res_digits, tuple):
                d = res_digits[1]
            else:
                d = res_digits(self.cr)[1]
        elif (hasattr(obj, '_field') and\
                isinstance(obj._field, (float_class, function_class)) and\
                obj._field.digits):
                d = obj._field.digits[1] or DEFAULT_DIGITS
        return d

    def execute(self, output_format='pdf', report_file_name=None):
        """
        Generate the report.
        """

        def _base64_to_string(field_value):
            """
            Helper method to decode a binary field
            """
            return base64.decodestring(field_value)

        def _get_attachments():
            """
            Helper function that returns a function that
            gets the attachments for one object using the current database
            connection (cr) and user (uid).
            """
            def get_attachments_func(browse_object):
                """
                Returns the attachments for one browse_object
                """
                db, pool = pooler.get_db_and_pool(self.dbname)
                cr = db.cursor()
                att_facade = pool.get('ir.attachment')
                # pylint: disable-msg=W0212
                attachment_ids = att_facade.search(cr, self.uid, [
                        ('res_model', '=', browse_object._name), 
                        ('res_id', '=', browse_object.id)
                    ])
                return att_facade.browse(cr, self.uid, attachment_ids)
            return get_attachments_func

        def _field_to_image(field_value, rotate=None):
            """
            Helper function that decodes and converts a binary field
            into a png image and returns a tuple like the ones Relatorio
            "image:" directive wants.
            """
            from PIL import Image
            data = base64.decodestring(field_value)
            dummy_fd, temp_file_name = tempfile.mkstemp(prefix='openerp_oor_f2i_')
            temp_file = open(temp_file_name, 'wb')
            try:
                temp_file.write(data)
            finally:
                temp_file.close()
            image = Image.open(temp_file_name)
            if rotate:
                image = image.rotate(rotate)
            image.save(temp_file_name, 'png')
            return (open(temp_file_name, 'rb'), 'image/png')


        def _chart_template_to_image(field=None, filename=None, source=None, filepath=None, source_format=None, encoding=None, context=None):
            """
            Method that can be referenced from the template to include
            charts as images.
            When called it will process the file as a chart template,
            generate a png image, and return the data plus the mime type.
            """
            # Field is a binary field with a base64 encoded file that we will
            # use as source if it is specified
            source = field and base64.decodestring(field) or source

            filepath = filepath or filename
            filename = None
            assert filepath

            #
            # Search for the file on the addons folder of OpenERP if the
            # filepath does not exist.
            #
            if not os.path.exists(filepath):
                search_paths = ['./bin/addons/%s' % filepath, './addons/%s' % filepath]
                for path in search_paths:
                    if os.path.exists(path):
                        filepath = path
                        break

            #
            # Genshi Base Template nor it's subclases
            # (NewTextTemplate and chart.Template)
            # seem to load the filepath/filename automatically;
            # so we will read the file here if needed.
            #
            if not source:
                file = open(filepath, 'rb')
                try:
                    source = file.read()
                finally:
                    file.close()

            #
            # Process the chart subreport file
            #
            self.log("Generating chart subreport...")
            from relatorio.templates.chart import Template
            chart_subreport_template = Template(source=source, encoding=encoding)
            data = chart_subreport_template #.generate(**context)
            self.log("...done, chart generated.")

            return (data, 'image/png')


        def _formatLang():
            """
            Helper function that returns a function that
            formats received value to the language format.
            """
            def _format_lang(value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False):
                """
                    Assuming 'Account' decimal.precision=3:
                        formatLang(value) -> digits=2 (default)
                        formatLang(value, digits=4) -> digits=4
                        formatLang(value, dp='Account') -> digits=3
                        formatLang(value, digits=5, dp='Account') -> digits=5
                """
                if digits is None:
                    if dp:
                        digits = self.get_digits(dp=dp)
                    else:
                        digits = self.get_digits(value)

                if isinstance(value, (str, unicode)) and not value:
                    return ''

                if not self.lang_dict_called:
                    self._get_lang_dict()
                    self.lang_dict_called = True

                if date or date_time:
                    if not str(value):
                        return ''

                    date_format = self.lang_dict['date_format']
                    parse_format = DT_FORMAT
                    if date_time:
                        value=value.split('.')[0]
                        date_format = date_format + " " + self.lang_dict['time_format']
                        parse_format = DHM_FORMAT
                    if not isinstance(value, time.struct_time):
                        return time.strftime(date_format, time.strptime(value, parse_format))

                    if not isinstance(value, time.struct_time):
                        try:
                            date = mx.DateTime.strptime(str(value),parse_format)
                        except:# sometimes it takes converted values into value, so we dont need conversion.
                            return str(value)
                    else:
                        date = datetime(*value.timetuple()[:6])
                    return date.strftime(date_format)

                return self.lang_dict['lang_obj'].format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)
            return _format_lang


        def _format(text, oldtag=None):
            """
            Removes white spaces
            """
            return text.strip()


        def translate():
            def _translate(text):
                lang = self.context['lang']
                if lang and text and not text.isspace():
                    transl_obj = self.pool.get('ir.translation')
                    piece_list = self._transl_regex.split(text)
                    for pn in range(len(piece_list)):
                        if not self._transl_regex.match(piece_list[pn]):
                            source_string = piece_list[pn].replace('\n', ' ').strip()
                            if len(source_string):
                                translated_string = transl_obj._get_source(self.cr, self.uid, self.name, ('report', 'rml'), lang, source_string)
                                if translated_string:
                                    piece_list[pn] = piece_list[pn].replace(source_string, translated_string)
                    text = ''.join(piece_list)
                return text
            return _translate


        def set_html_image():
            def _set_htmlImage(id, model=None, field=None, context=None):
                if not id :
                    return ''
                if not model:
                    model = 'ir.attachment'
                try :
                    id = int(id)
                    res = self.pool.get(model).read(self.cr,self.uid,id)
                    if field :
                        return res[field]
                    elif model =='ir.attachment' :
                        return res['datas']
                    else:
                        return ''
                except Exception,e:
                    return ''

            return _set_htmlImage

        def setLang():
            """set lang to context"""
            self.context['lang'] = lang
            self.lang_dict_called = False



        assert output_format

        #
        # Get the report path
        #
        if not report_file_name:
            reports = self.pool.get( 'ir.actions.report.xml' )
            report_ids = reports.search(self.cr, self.uid, [('report_name', '=', self.name[7:])], context=self.context)
            report_file_name = reports.read(self.cr, self.uid, report_ids[0], ['report_rml'])['report_rml']
            path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
            report_file_name = os.path.join(path, report_file_name)

        #
        # Set the variables that the report must see
        #
        context = self.context
        context['objects'] = self.pool.get(self.model).browse(self.cr, self.uid, self.ids, self.context)
        context['ids'] = self.ids
        context['model'] = self.model
        context['data'] = self.data

        #
        # Some aliases used on standard OpenERP reports
        #
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context)
        context['user'] = user
        context['company'] = user.company_id
        context['logo'] = user.company_id and user.company_id.logo
        context['lang'] = context.get('lang') or (user.company_id and user.company_id.partner_id and user.company_id.partner_id.lang)

        #
        # Add some helper function aliases
        #
        context['base64_to_string'] = context.get('base64_to_string') or _base64_to_string
        context['b2s'] = context.get('b2s') or _base64_to_string
        context['get_attachments'] = context.get('get_attachments') or _get_attachments()
        context['field_to_image'] = context.get('field_to_image') or _field_to_image
        context['f2i'] = context.get('f2i') or _field_to_image
        context['chart_template_to_image'] = context.get('chart_template_to_image') or _chart_template_to_image
        context['chart'] = context.get('chart') or _chart_template_to_image
        context['translate'] = context.get('translate') or translate()
        context['_'] = context.get('_') or translate()
        context['formatLang'] = context.get('formatLang') or _formatLang()
        context['format'] = context.get('format') or _format
        context['setHtmlImage'] = context.get('setHtmlImage') or set_html_image()
        context['time'] = context.get('time') or time
        context['setLang'] = context.get('setLang') or setLang

        # Update the context with the custom report context
        context.update(self.get_report_context())

        #
        # Process the template using the OpenOffice/Relatorio engine
        #
        data = self.process_template(report_file_name, output_format, context)

        return data

    def process_template(self, template_file, output_format, context=None):
        """
        Will process a relatorio template and return the name
        of the temp output file.
        """
        if context is None: context = {}
        #
        # Get the template
        #
        self.log("Loading template %s from %s" % (self.name, template_file))
        try:
            template = OOTemplate(source=None,
                            filepath=template_file,
                            output_format=output_format,
                            openoffice_port=self.openoffice_port,
                            autostart_openoffice=self.autostart_openoffice,
                            logger=self.log)
        except OOTemplateException, ex:
            raise OOReportException(_("Error loading the OpenOffice template: %s") % ex)

        #
        # Process the template
        #
        self.log("Rendering template %s as %s" % (self.name, output_format))
        try:
            data = template.oo_render(context=context)
        except OOTemplateException, ex:
            raise OOReportException(_("Error processing the OpenOffice template: %s") % ex)

        return data



class openoffice_report(report.interface.report_int):
    """
    Registers an OpenOffice/Relatorio report.
    """

    def __init__(self, name, model, parser=None, context=None):
        if context is None: context = {}
        # Remove report name from list of services if it already
        # exists to avoid report_int's assert. We want to keep the
        # automatic registration at login, but at the same time we
        # need modules to be able to use a parser for certain reports.
        if not name.startswith('report.'):
            name = 'report.' + name
        if name in netsvc.Service._services:
            del netsvc.Service._services[name]
        super(openoffice_report, self).__init__(name)
        
        self.model = model
        self.parser = parser
        self._context = context

    def create(self, cr, uid, ids, datas, context=None):
        """
        Register the report with this handler.
        """
        name = self.name

        reportClass = self.parser or OOReport


        self._context.update(context)

        #
        # Find the output format
        #
        reports = pooler.get_pool(cr.dbname).get( 'ir.actions.report.xml' )
        report_ids = reports.search(cr, uid, [('report_name', '=', name[7:])], context=context)
        report_type = reports.read(cr, uid, report_ids[0], ['report_type'])['report_type']
        if report_type.startswith('oo-'):
            output_format = report_type.split('-')[1]
        else:
            output_format = 'pdf'

        #
        # Get the report
        #
        rpt = reportClass( name, cr, uid, ids, datas, self._context )
        return (rpt.execute(output_format=output_format), output_format )


#Allow calling to old create method...
if 'old_create' not in dir(report.report_sxw.report_sxw):
    report.report_sxw.report_sxw.old_create = report.report_sxw.report_sxw.create 


def create(self, cr, uid, ids, data, context=None):
    """
    Wrapper around the create method of report_sxw
    that registers 'automagically' OpenOffice reports.
    """
    if context is None: context = {}
    if self.internal_header:
        context.update({'internal_header': self.internal_header})
    
    fnct_ret = False
    report_type= data.get('report_type', 'pdf')

    if not report_type.startswith('oo-'):
        fnct_ret = self.old_create(cr, uid, ids, data, context=context)
    else:
        oo_report = openoffice_report(self.name, data['model'], context=context)
        fnct_ret = oo_report.create(cr, uid, ids, data, context)
        if not fnct_ret:
            return (False,False)

    return fnct_ret

#override create method
report.report_sxw.report_sxw.create = create

