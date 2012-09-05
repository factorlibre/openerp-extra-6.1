# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenOffice Reports
#    Copyright (C) 2009 Pexego Sistemas Informáticos. All Rights Reserved
#    Based on Relatorio (see http://relatorio.openhex.org/)
#       and PyODConverter (http://www.artofsolving.com/opensource/pyodconverter)
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
OpenOffice/Relatorio template engine.
"""
__author__ = "Borja López Soilán (Pexego)"

from tools.translate import _
import os
import tempfile
import inspect
import base64
import subprocess
import time
import genshi
from os.path import abspath, splitext
from relatorio.templates.opendocument import Template


class OOTemplateException(Exception):
    """
    OpenOffice template exception
    """
    def __init__(self, message):
        # pylint: disable-msg=W0231
        self.message = message
    def __str__(self):
        return self.message


class OOTemplate(Template):
    """
    OpenOffice/Relatorio template.
    Extends the standard relatorio template to let the user include subreports
    with the "${ subreport(file, context) }" statement,
    and allow file conversions (pdf output and such).

    Note: It needs an OpenOffice instance running and listening for the
    advanced features.
    """

    def log(self, message):
        """
        Helper method used print debug messages
        """
        if self.logger:
            self.logger(message)
        else:
            print "OOTemplate: %s" % message
        

    def __init__(self, source=None, filepath=None, filename=None, loader=None,
                 encoding=None, lookup='strict', allow_exec=True,
                 source_format=None, output_format=None,
                 openoffice_port=8100, autostart_openoffice=True,
                 logger=None):
        """
        Init the oo_subreports list, OpenOffice options and formats,
        and then delegate on the parent constructor.
        """
        self.logger = logger

        self.temp_file_names = [] # List of files to delete on the destructor (__del__)
        assert filepath or filename or source_format

        if source:
            #
            # Relatorio reports don't support using source instead of filepath/filename.
            # Passing the file contents using source seems useful, but
            # we will have to write it somewhere for Relatorio to work.
            # So we will create a temp file (that will be removed when
            # oo_render ends, and dump source to that file.
            #
            assert isinstance(source, (file, str, unicode))
            self.log("Template is a file-like object or string, writing it to a temp file.")
            dummy_fd, temp_file_name = tempfile.mkstemp(suffix=".%s" % source_format, prefix='openerp_oot_t_')
            temp_file = open(temp_file_name, 'wb')
            try:
                if isinstance(source, file):
                    temp_file.write(source.read())
                elif isinstance(source, (str, unicode)):
                    temp_file.write(source)
            finally:
                temp_file.close()
            self.temp_file_names.append(temp_file_name)
            filepath = temp_file_name

        filepath = filepath or filename
        filename = None
        assert filepath

        if not os.path.exists(filepath):
            search_paths = ['./bin/addons/%s' % filepath, './addons/%s' % filepath]
            for path in search_paths:
                if os.path.exists(path):
                    filepath = path
                    break

        if not source_format:
            # Get the source_format from the file name:
            source_format = splitext(filepath or filename)[1][1:]

        assert source_format and output_format
        source_format = source_format.lower()
        output_format = output_format.lower()

        if source_format in ('doc', 'rtf', 'txt', 'xls'):
            # It's not an OpenDocument file,
            # (it may be a Microsoft Word document [doc] for example),
            # convert it using OpenOffice.
            format_mapping = { 'doc': 'odt', 'rtf': 'odt', 'txt': 'odt', 'xls': 'ods'}
            self.log("Template file is not an OpenDocument, converting from %s to %s." % (source_format, format_mapping[source_format]))
            dummy_fd, temp_file_name = tempfile.mkstemp(suffix=".%s" % format_mapping[source_format], prefix='openerp_oot_t_')
            oohelper = OOHelper(openoffice_port, autostart_openoffice, logger=self.logger)
            document = oohelper.open_document(filepath)
            oohelper.save_document(document, temp_file_name, close_document=True)
            self.temp_file_names.append(temp_file_name)
            source_format = format_mapping[source_format]
            filepath = temp_file_name

        self.source_format = source_format
        self.output_format = output_format
        self.openoffice_port = openoffice_port
        self.autostart_openoffice = autostart_openoffice
        self.oo_subreports = []

        super(OOTemplate, self).__init__(source, filepath, filename, loader,
                                       encoding, lookup, allow_exec)


    def __del__(self):
        """
        Destructor of the template: Will delete any temp file created on the
        constructor.
        """
        if self.temp_file_names:
            for file_name in self.temp_file_names:
                os.unlink(file_name)


    def generate(self, *args, **kwargs):
        """
        Apply the template to the given context data.
        Overwrites the generate method to add support for subreports.
        Delegates on the standard generate method for everything else.
        """
        def _subreport(field=None, filename=None, source=None, filepath=None, source_format=None, encoding=None, context=None):
            """
            Method that can be referenced from the template to include subreports.
            When called it will process the file as a template,
            write the generated data to a temp file, 
            and return a reference (filename) to this output file for later usage.
            The OOTemplate will will use this data, after the main template
            is generated, to do an insertion pass using UNO.
            """
            # Field is a binary field with a base64 encoded file that we will
            # use as source if it is specified
            source = field and base64.decodestring(field) or source

            #
            # Get the current report context so the subreport can see
            # the variables defined on the report.
            #
            if not context:
                context = {}
                try:
                    frame = inspect.stack()[1][0]
                    locals_context = frame.f_locals.copy()
                    data_context = locals_context.get('__data__') or context
                    if data_context and isinstance(data_context, genshi.template.base.Context):
                        for c in data_context.frames:
                            context.update(c)
                    else:
                        context = data_context
                except:
                    self.log("Warning: Failed to get the context for the subreport from the stack frame!")


            # Get the source_format from the file name:
            if not source_format and (filepath or filename):
                source_format = splitext(filepath or filename)[1][1:]
            source_format = source_format or self.source_format
            assert source_format

            #
            # Process the subreport file like a normal template
            # (we are recursive!)
            #
            self.log("Generating subreport (%s)..." % source_format)
            subreport_template = OOTemplate(source=source,
                                filepath=filepath,
                                filename=filename,
                                encoding=encoding,
                                source_format=source_format,
                                output_format=self.source_format,
                                openoffice_port=self.openoffice_port,
                                autostart_openoffice=self.autostart_openoffice,
                                logger=self.log)
            data = subreport_template.oo_render(context)

            #
            # Save the subreport data to a temp file
            #
            dummy_fd, temp_file_name = tempfile.mkstemp(suffix=".%s" % source_format, prefix='openerp_oot_s_')
            temp_file = open(temp_file_name, 'wb')
            try:
                temp_file.write(data)
            finally:
                temp_file.close()

            #
            # Save a reference to this file for later usage
            #
            self.oo_subreports.append(temp_file_name)
            self.log("...subreport generated as %s." % temp_file_name)

            # Return a placeholder that will be replaced later,
            # on the insertion step, with the file contents:
            return "${insert_doc('%s')}" % temp_file_name

        # Add the include function to the report context
        kwargs['subreport'] = _subreport

        # Generate the template
        res = super(OOTemplate, self).generate(*args, **kwargs)

        return res



    def oo_render(self, context=None):
        """
        Wrapper, around the render method of the original template,
        that adds support for subreports and format conversion.
        The wrapper is required as these operations need to be performed,
        using OpenOffice, after the document generation by the template.
        """
        if context is None: context = {}
        self.log("Generating report: step 1...")

        # Generate the stream from the template (Relatorio)
        data = self.generate(**context).render().getvalue()

        self.log("...step 1 done.")

        #
        # Next steps need OpenOffice to perform some tasks
        # like file insertion or format conversions.
        # Using OpenOffice brings some overhead, so we will try to avoid
        # connecting to it unless it is necesary.
        #
        if len(self.oo_subreports)>0 or (self.output_format != self.source_format):
            self.log("Step 2....")

            # Connect to OpenOffice
            oohelper = OOHelper(self.openoffice_port, self.autostart_openoffice, logger=self.log)

            #
            # Create a temporary (input for OpenOffice) file
            #
            dummy_fd, temp_file_name = tempfile.mkstemp(suffix=".%s" % self.source_format, prefix='openerp_oot_i_')
            temp_file = open(temp_file_name, 'wb')
            try:
                #
                # Write the data to the file
                #
                try:
                    temp_file.write(data)
                finally:
                    temp_file.close()

                # Reopen the file with OpenOffice
                document = oohelper.open_document(temp_file_name)

                #
                # Insert subreport files if needed
                #
                if len(self.oo_subreports)>0:
                    self.log("Inserting subreport files")
                    for subreport in self.oo_subreports:
                        placeholder_text = "${insert_doc('%s')}" % subreport
                        oohelper.replace_text_with_file_contents(document, placeholder_text, subreport)
                        # Remove the subreport temp file
                        os.unlink(subreport)

                #
                # Save the file (does the format conversion) on a temp file
                #
                dummy_fd, output_file_name = tempfile.mkstemp(suffix=".%s" % self.output_format, prefix='openerp_oot_o_')
                try:
                    # Save the document
                    oohelper.save_document(document, output_file_name, close_document=True)

                    #
                    # Read back the data
                    #
                    output_file = open(output_file_name, 'rb')
                    try:
                        data = output_file.read()
                    finally:
                        output_file.close()
                finally:
                    # Remove the temp file
                    os.unlink(output_file_name)
            finally:
                # Remove the temp file
                os.unlink(temp_file_name)

            self.log("...step 2 done.")


        # TODO: As a long term feature it would be nice to be able to tell OpenOffice to refresh/recalculate the Table Of Contents (if there is any)


        # Return the data (byte string)
        return data




class OOHelperException(Exception):
    """
    OpenOffice template exception
    """
    def __init__(self, message):
        # pylint: disable-msg=W0231
        self.message = message
    def __str__(self):
        return self.message



class OOHelper():
    """
    OpenOffice helper methods.

    Loads and saves OpenOffice documents, doing the needed format conversions.
    Also lets you to replace text (placeholders) on documents with the contents
    of another document.

    Uses PyUNO, requires OpenOffice to be installed on the computer,
    and a OpenOffice instance listening on the given port
    (or it may start a headless OpenOffice instance for you).

    Based on PyODConverter (http://www.artofsolving.com/opensource/pyodconverter)
    """

    # OpenOffice main executable posible paths
    OOPATHS = [ '/usr/bin/soffice', '/usr/lib64/ooo-2.0/program/soffice', '/opt/openoffice.org3/program/soffice', 'C:\\Program Files\\OpenOffice.org 3.1\\program\\soffice', ]


    #
    # Import/export formats and filter options
    #
    # see http://wiki.services.openoffice.org/wiki/Framework/Article/Filter
    #

    #
    # Import filter options (only formats that require options)
    #
    IMPORT_FILTER_MAP = {
        'txt': { 'FilterName': 'Text (encoded)', 'FilterOptions': 'utf8' },
        'csv': { 'FilterName': 'Text - txt - csv (StarCalc)', 'FilterOptions': '44,34,0' }
    }

    #
    # Export filter mapping
    #
    EXPORT_FILTER_MAPS = {
        'text': {
            'pdf':      { "FilterName": "writer_pdf_Export" },
            'html':     { "FilterName": "HTML (StarWriter)" },
            'odt':      { "FilterName": "writer8" },
            'doc':      { "FilterName": "MS Word 97" },
            'rtf':      { "FilterName": "Rich Text Format" },
            'txt':      { "FilterName": "Text", "FilterOptions": "utf8" }
        },
        'web': {
            'pdf':      { "FilterName": "writer_web_pdf_Export" },
            'odt':      { "FilterName": "writerweb8_writer" },
        },
        'spreadsheet': {
            'pdf':      { "FilterName": "calc_pdf_Export" },
            'html':     { "FilterName": "HTML (StarCalc)" },
            'ods':      { "FilterName": "calc8" },
            'xls':      { "FilterName": "MS Excel 97" },
            'csv':      { "FilterName": "Text - txt - csv (StarCalc)", "FilterOptions": "44,34,0" }
        },
        'presentation': {
            'pdf':      { "FilterName": "impress_pdf_Export" },
            'html':     { "FilterName": "impress_html_Export" },
            'odp':      { "FilterName": "impress8" },
            'ppt':      { "FilterName": "MS PowerPoint 97" },
            'ppt':      { "FilterName": "impress_flash_Export" },
        },
        'drawing': {
            'pdf':      { "FilterName": "draw_pdf_Export" },
            'swf':      { "FilterName": "draw_flash_Export" },
        }
    }


    #
    # Code ---------------------------------------------------------------------
    #

    def log(self, message):
        """
        Helper method used print debug messages
        """
        if self.logger:
            self.logger(message)
        else:
            print "OOHelper: %s" % message


    def __init__(self, openoffice_port=8100, autostart_openoffice=True, logger=None):
        """
        Initialize the default values and try to connect to OpenOffice
        (or even start it).
        """
        import uno

        self.logger = logger

        self.port = openoffice_port
        self.autostart = autostart_openoffice

        #
        # Try to connect with retries (to start OpenOffice if autostart_openoffice is enabled)
        #
        retry = 2
        while retry:
            retry = retry - 1
            try:
                self.log("Connecting to OpenOffice...")
                local_component_context = uno.getComponentContext()
                resolver = local_component_context.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local_component_context)
                component_context = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % self.port)
                self.desktop = component_context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", component_context)
                self.log("...connected.")
            except Exception, ex:
                #
                # Assume that the connection to OpenOffice has failed
                # because OpenOffice is not running or listening
                # and try to start it if autostart_openoffice.
                #
                self.log("...connection to OpenOffice failed!")
                if autostart_openoffice and retry:
                    #
                    # Try to start a headless OpenOffice server
                    #
                    ooffice = None
                    for path in self.OOPATHS:
                        if os.path.exists(path):
                            ooffice = path
                            break
                    if ooffice:
                        self.log("Starting headless OpenOffice listener on port %s..." % self.port)
                        subprocess.call([ooffice, '-headless', '-nofirststartwizard', '-accept=socket,host=localhost,port=%s;urp;' % self.port])
                        # Wait for OO to start
                        time.sleep(5)
                        self.log("...trying again...")
                else:
                    raise OOHelperException(_("Couldn't connect to OpenOffice. Make sure you have an OpenOffice instance running and listening on the %s port. Details: %s") % (self.port, (hasattr(ex, 'value') and str(ex.value) or str(ex))))


    def open_document(self, file_name):
        """
        Opens a document with OpenOffice
        """
        import uno
        file_url = uno.systemPathToFileUrl(abspath(file_name))

        if os.environ.get('OSTYPE', False) == 'FreeBSD':
            # Workaround a problemas con OpenOffice 3.1 en FreeBSD
            file_url = file_url.encode('UTF-8')

        load_properties = { "Hidden": True }
        file_ext = splitext(file_name)[1]
        file_ext = file_ext and file_ext[1:].lower() or None
        if self.IMPORT_FILTER_MAP.has_key(file_ext):
            load_properties.update(self.IMPORT_FILTER_MAP[file_ext])

        try:
            document = self.desktop.loadComponentFromURL(file_url, "_blank", 0, self.make_properties(load_properties))
        except Exception, ex:
            raise OOHelperException(_("Error loading file %s with OpenOffice: %s") % (file_name, ex))
        try:
            document.refresh()
        except AttributeError:
            #print "Warning: Ignoring AttributeError on document refresh"
            pass

        return document


    def save_document(self, document, file_name, close_document=True):
        """
        Saves a OpenOffice document to a file.
        The file format will be detected (based on the file extension)
        and the document will be converted to that format (see EXPORT_FILTER_MAPS).
        """
        import uno
        file_url = uno.systemPathToFileUrl(abspath(file_name))
        
        if os.environ.get('OSTYPE', False) == 'FreeBSD':
            # Workaround a problemas con OpenOffice 3.1 en FreeBSD
            file_url = file_url.encode('UTF-8')

        save_properties = { }

        #
        # Get the export filter options for the given file extension
        #
        file_ext = splitext(file_name)[1]
        file_ext = file_ext and file_ext[1:].lower() or None

        export_filter_map = \
                (document.supportsService("com.sun.star.text.WebDocument") and self.EXPORT_FILTER_MAPS['web']) \
                or (document.supportsService("com.sun.star.text.GenericTextDocument") and self.EXPORT_FILTER_MAPS['text']) \
                or (document.supportsService("com.sun.star.sheet.SpreadsheetDocument") and self.EXPORT_FILTER_MAPS['spreadsheet']) \
                or (document.supportsService("com.sun.star.presentation.PresentationDocument") and self.EXPORT_FILTER_MAPS['presentation']) \
                or (document.supportsService("com.sun.star.drawing.DrawingDocument") and self.EXPORT_FILTER_MAPS['drawing'])

        if export_filter_map and export_filter_map.has_key(file_ext):
            save_properties.update(export_filter_map[file_ext])

        #
        # Save the document
        #
        try:
            document.storeToURL(file_url, self.make_properties(save_properties))
        except Exception, ex:
            raise OOHelperException(_("Error saving file %s with OpenOffice: %s") % (file_name, ex))
        finally:
            if close_document:
                document.close(True)



    def replace_text_with_file_contents(self, document, placeholder_text, file_name):
        """
        Inserts the given file into the current document.
        The file contents will replace the placeholder text.
        """
        import uno
        file_url = uno.systemPathToFileUrl(abspath(file_name))

        search = document.createSearchDescriptor()
        search.SearchString = placeholder_text

        found = document.findFirst( search )
        while found:
            try:
                found.insertDocumentFromURL(file_url, ())
            except Exception, ex:
                raise OOHelperException(_("Error inserting file %s on the OpenOffice document: %s") % (file_name, ex))
            found = document.findNext(found, search)


    def make_properties(self, properties_dict):
        """
        Helper to create a tuple of PropertyValue items from a dictionary.
        """
        import uno
        props = []
        for key in properties_dict:
            prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
            prop.Name = key
            prop.Value = properties_dict[key]
            props.append(prop)
        return tuple(props)



