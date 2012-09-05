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
#
# OpenOffice Reports - Reporting Engine based on Relatorio and OpenOffice.
#
# Autor: Borja López Soilán (Pexego)
#
{
        "name" : "Pexego OpenOffice Reports",
        "version" : "0.2",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """Pexego OpenOffice Reports - Reporting Engine based on Relatorio and OpenOffice.

Reporting engine that uses OpenOffice and Relatorio to create reports from several kind of templates (like an OpenDocument Text, a Microsoft Excel spreadsheet, or even a PowerPoint!) 
and export them on several formats (i.e.: it may create a Microsoft Excel spreadsheet from a OpenDocument spreadshet template).

Based on Relatorio (see http://relatorio.openhex.org/), PyODConverter (http://www.artofsolving.com/opensource/pyodconverter) and the Jasper Reports addon from Koo (https://code.launchpad.net/openobject-client-kde).


*** FEATURES ***

- The next template formats and output formats are supported:
  * Text (any text format supported by OpenOffice like odt, doc, rtf, txt): 
        pdf, html, odt, doc (MS Word 97), rtf, txt
  * Web (hmtl): 
        pdf, odt
  * Spreadsheet (ods, xls): 
        pdf, html, ods, xls (MS Excel 97), csv
  * Presentation (odp, ppt): 
        pdf, html, odp, ppt
  * Drawing (odg): 
        pdf, swf

- Subreports (inserting another file anywhere on the document) are supported for text formats,
  they are recursive (will be processed by the template system and may have their own subreports)
  and they can be loaded from a binary field.
  
- Dynamic insertion of images is supported too, and they can be loaded from a file or a binary field.

- Conditional statements (if) and repetitive structures (for) are supported. And they can be used in tables.


*** TEMPLATE LANGUAGE ***

Templates are based on Relatorio and Genshi, you might find useful this introduction to Relatorio: http://relatorio.openhex.org/wiki/IndepthIntroduction

Some additional features, mainly related to OpenERP, where added:

    - Support for subreports (text documents only).
        * From OpenObject binary fields:
            ${ subreport(object.file_field, object.filename_field) }
        * From files on disk:
            ${ subreport(filepath='/tmp/something.odt') }
        * From buffers (open files, strings):
            ${ subreport(source=buffer, source_format='odt') }

    - Translations using the OpenERP translation engine:
        ${ _("Object Name") }

    - Access to attachments of an OpenObject:
        * Get the attachment names:
            ${ ', '.join([a.name for a in get_attachments(object)]) }
        * Use the first attachment as a subreport (only text documents):
            ${ subreport(get_attachments(object)[0].datas, get_attachments(object)[0].datas_fname) }

    - Using images from fields:
        * On a frame name (see Relatorio documentation about including images),
            instead of "image: (file, mimetype)'",
            use "image: ${ field_to_image(object.field) }"


*** REQUIREMENTS ***

- Relatorio (0.5.0 or better) for basic templating (odt->odt and ods->ods only),
- OpenOffice (2.4 or better) and PyUno for file conversions and subreports.
- Python Imaging Library (PIL) if you want to use images from binary fields.
- PyCha (3.0 or better) if you want to use charts.
- Genshi (0.5.1 or better) for using ${} instead of relatorio://

        """,
        "depends" : [
                     'base',
                     ],
        "init_xml" : [],
        "demo_xml" : [
                     'demo/partner_demo_report.xml',
                     ],
        "update_xml" : [
                     'security/ir.model.access.csv',
                     'report_xml_view.xml',
                        ],
        "installable": True
}
