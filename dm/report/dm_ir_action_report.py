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
from osv import fields, osv
import pooler
import os
from dm_document_report import offer_document
from base_report_designer.wizard.tiny_sxw2rml import sxw2rml
from report.report_sxw import report_sxw, sxw_parents, sxw_tag
from report import interface
from StringIO import StringIO
import base64
import re
import tools
from lxml import etree
from zipfile import ZipFile

_regex = re.compile('\[\[setHtmlImage\((.+?)\)\]\]')

#class my_report_sxw(report_sxw):
#    def create_single(self, cr, uid, ids, data, report_xml, context={}):
#        report_sxw.create_single(self, cr, uid, ids, data, report_xml, context)


class report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'document_id': fields.integer('Document'),
       'report_type' : fields.selection([
            ('pdf', 'pdf'),
            ('html', 'html'),
            ('raw', 'raw'),
            ('sxw', 'sxw'),
            ('odt', 'odt'),
            ('html2html','Html from html'),
            ("oo_pdf","OO - PDF"),
            ("oo_doc","OO - MS Word 97"),
            ("oo_rtf","OO - Rich Text Format"),
            ("oo_html","OO - HTML"),
            ("oo_txt","OO - Text"),
            ], string='Type', required=True),
        }

    def register_all(self, cr):
        opj = os.path.join
        result=''
        cr.execute("SELECT * FROM ir_act_report_xml WHERE model=%s \
                        ORDER BY id", ('dm.offer.document',))
        result = cr.dictfetchall()
        for r in result:
            if netsvc.service_exist('report.'+r['report_name']):
                continue
            if r['report_rml'] or r['report_rml_content_data']:
                report_sxw('report.'+r['report_name'], r['model'],
                        opj('addons',r['report_rml'] or '/'), header=r['header'],
                        parser=offer_document)

        super(report_xml, self).register_all(cr)

    def upload_report(self, cr, uid, report_id, file_sxw,file_type, context):
        '''
        Untested function
        '''
        pool = pooler.get_pool(cr.dbname)
        sxwval = StringIO(base64.decodestring(file_sxw))
        if file_type == 'sxw':
            fp = tools.file_open('normalized_oo2rml.xsl',
                    subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
            rml_content = str(sxw2rml(sxwval, xsl=fp.read()))
        if file_type == 'odt':
            fp = tools.file_open('normalized_odt2rml.xsl',
                    subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
            rml_content = str(sxw2rml(sxwval, xsl=fp.read()))
        if file_type == 'html':
            rml_content = base64.decodestring(file_sxw)
        report = pool.get('ir.actions.report.xml').write(cr, uid, [report_id], {
            'report_sxw_content': base64.decodestring(file_sxw),
            'report_rml_content': rml_content,
        })
        cr.commit()
        db = pooler.get_db_only(cr.dbname)
        interface.register_all(db)
        return True

    def set_image_email(self, cr, uid, report_id):
        list_image_id = []
        def process_tag(node, list_image_id):
            if not node.getchildren():
                if  node.tag=='img' and node.get('name'):
                    if node.get('name').find('setHtmlImage') >= 0:
                        res_id= _regex.split(node.get('name'))[1]
                        list_image_id.append((res_id,node.get('src')))
                    if node.get('name').find('http') >= 0:
                        list_image_id.append(('URL,%s'%node.get('name'),node.get('src')))
            else:
                for n in node.getchildren():
                    process_tag(n, list_image_id)
        datas = self.report_get(cr, uid, report_id)['report_sxw_content']
        root = etree.HTML(base64.decodestring(datas))
        process_tag(root, list_image_id)
        return list_image_id

report_xml()
try:
    from UNOConverter import DocumentConverter
    converter = DocumentConverter()
except Exception,e:
    converter=None
# over rider report_sxw class
def create_oo_report(self, cr, uid, ids, data, report_xml, context=None):
    if not context:
        context={}
    context = context.copy()
    context['parents'] = sxw_parents
    sxw_io = StringIO(report_xml.report_sxw_content)
    sxw_z = ZipFile(sxw_io, mode='r')
    rml = sxw_z.read('content.xml')
    meta = sxw_z.read('meta.xml')
    mime_type = sxw_z.read('mimetype')
    sxw_z.close()
    if mime_type == 'application/vnd.sun.xml.writer':
        mime_type = 'sxw'
    else:
        mime_type = 'odt'

    rml_parser = self.parser(cr, uid, self.name2, context=context)
    rml_parser.parents = sxw_parents
    rml_parser.tag = sxw_tag
    objs = self.getObjects(cr, uid, ids, context)
    rml_parser.set_context(objs, data, ids,mime_type)
    rml_dom_meta = node = etree.XML(meta)
    elements = node.findall(rml_parser.localcontext['name_space']["meta"]+"user-defined")
    for pe in elements:
        if pe.get(rml_parser.localcontext['name_space']["meta"]+"name"):
            if pe.get(rml_parser.localcontext['name_space']["meta"]+"name") == "Info 3":
                pe[0].text=data['id']
            if pe.get(rml_parser.localcontext['name_space']["meta"]+"name") == "Info 4":
                pe[0].text=data['model']
    meta = etree.tostring(rml_dom_meta, encoding='utf-8',
                          xml_declaration=True)

    rml_dom =  etree.XML(rml)
    body = rml_dom[-1]
    elements = []
    key1 = rml_parser.localcontext['name_space']["text"]+"p"
    key2 = rml_parser.localcontext['name_space']["text"]+"drop-down"
    key3 = rml_parser.localcontext['name_space']["text"]+"span"
    for n in rml_dom.iterdescendants():
        if n.tag == key1:
            elements.append(n)
    for pe in elements:
        e = pe.iterfind(key2)
        for de in e:
            new_text = de.text or ''
            for cnd in de:
                text = cnd.get(rml_parser.localcontext['name_space']["text"]+"value",False)
                new_text += text.startswith('[[') and text or ''
            new_text += de.tail or ''
            if new_text :
                new_node = de.getparent().makeelement(rml_parser.localcontext['name_space']["text"]+"span")
                new_node.text =  new_text
                de.getparent().replace(de,new_node)
    for pe in elements:
        e = pe.findall(key3)
        for span in e:
            new_text = span.text or ''
            for de in span.getchildren():
                new_text += de.text or ''
                for cnd in de.getchildren():
                    text = cnd.get(rml_parser.localcontext['name_space']["text"]+"value",False)
                    new_text += text.startswith('[[') and text or ''
                new_text += de.tail or ''
                span.remove(de)
            span.text = new_text
    import time
    rml_dom = self.preprocess_rml(rml_dom,mime_type)
    start_time = time.time()
    create_doc = self.generators[mime_type]
    odt = etree.tostring(create_doc(rml_dom, rml_parser.localcontext),encoding='utf-8', xml_declaration=True)
    sxw_z = ZipFile(sxw_io, mode='a')
    sxw_z.writestr('content.xml', odt)
    sxw_z.writestr('meta.xml', meta)

    if report_xml.header:
        #Add corporate header/footer
        rml = tools.file_open(os.path.join('base', 'report', 'corporate_%s_header.xml' % mime_type)).read()
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        rml_parser.parents = sxw_parents
        rml_parser.tag = sxw_tag
        objs = self.getObjects(cr, uid, ids, context)
        rml_parser.set_context(objs, data, ids, report_xml.mime_type)
        rml_dom = self.preprocess_rml(etree.XML(rml),mime_type)
        create_doc = self.generators[mime_type]
        odt = create_doc(rml_dom,rml_parser.localcontext)
        if report_xml.header:
            rml_parser._add_header(odt)
        odt = etree.tostring(odt, encoding='utf-8',
                             xml_declaration=True)
        sxw_z.writestr('styles.xml', odt)
    sxw_z.close()
    final_op = sxw_io.getvalue()
    report_type = report_xml.report_type[3:]
    if report_type != mime_type:
        if not converter:
            final_op = None
        else :
            start_time = time.time()
            final_op = converter.storeByPath(final_op, report_type)
    sxw_io.close()        
    return (final_op, report_type)

def create(self, cr, uid, ids, data, context=None):
    pool = pooler.get_pool(cr.dbname)
    ir_obj = pool.get('ir.actions.report.xml')
    report_xml_ids = ir_obj.search(cr, uid,
            [('report_name', '=', self.name[7:])], context=context)
    if report_xml_ids:
        report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
    else:
        title = ''
        rml = tools.file_open(self.tmpl, subdir=None).read()
        report_type= data.get('report_type', 'pdf')
        class a(object):
            def __init__(self, *args, **argv):
                for key,arg in argv.items():
                    setattr(self, key, arg)
        report_xml = a(title=title, report_type=report_type, report_rml_content=rml, name=title, attachment=False, header=self.header)
    report_type = report_xml.report_type
    if report_type in ['sxw','odt']:
        fnct_ret = self.create_source_odt(cr, uid, ids, data, report_xml, context)
    elif report_type in ['pdf','raw','html']:
        fnct_ret = self.create_source_pdf(cr, uid, ids, data, report_xml, context)
    elif report_type=='html2html':
        fnct_ret = self.create_source_html2html(cr, uid, ids, data, report_xml, context)
    elif report_type in ["oo_pdf","oo_doc","oo_rtf","oo_html","oo_txt"]:
        fnct_ret = create_oo_report(self, cr, uid, ids, data, report_xml, context)
    else:
        raise 'Unknown Report Type'
    if not fnct_ret:
        return (False,False)
    return fnct_ret
report_sxw.create =  create    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:      

