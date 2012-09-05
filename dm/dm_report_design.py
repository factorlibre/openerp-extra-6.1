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

from osv import osv
import pooler
import netsvc

from plugin.customer_function import customer_function
from plugin.dynamic_text import dynamic_text
from plugin.php_url import php_url

import re
import time
import base64
import os
import sys
import tools

# To Fix: use no style css, no static values, en-IN ??
internal_html_report = u'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
    <TITLE></TITLE>
    <META NAME="GENERATOR" CONTENT="OpenOffice.org 3.0  (Linux)">
    <META NAME="CREATED" CONTENT="20090420;15063300">
    <META NAME="CHANGED" CONTENT="20090420;15071700"> 
    <META NAME="Info 4" CONTENT="dm.offer.document">
    <STYLE TYPE="text/css">
        <!--
        @page { margin: 2cm }
        P { margin-bottom: 0.21cm }
        A:link { so-language: zxx }
        -->
    </STYLE>
</HEAD>
<BODY LANG="en-IN" DIR="LTR">
'''

def merge_message(cr, uid, keystr, context): # {{{
    " Merge offer internal document content and plugins values "
    def merge(match):
        exp = str(match.group()[2:-2]).strip()
        if exp not in context :
            dm_obj = pooler.get_pool(cr.dbname).get('dm.offer.document')
            obj = dm_obj.browse(cr, uid, context.get('document_id'))
            args = context.copy()
            if 'plugin_list' in context :
                args['plugin_list'] = context['plugin_list']
            else :
                args['plugin_list'] = [exp]
            plugin_values = generate_plugin_value(cr, uid, **args)
            context.update(plugin_values)
            context.update({'object':obj, 'time':time})
        result = eval(exp, context)
        return result
    com = re.compile('(\[\[.+?\]\])')
    context['plugin_list'] = map(lambda x:x[2:-2].strip(),com.findall(keystr))
    message = com.sub(merge, keystr)
    return message # }}}
    
def generate_internal_reports(cr, uid, report_type, 
                              document_data, camp_doc, context): # {{{

    "Generate documents from the internal editor"
    pool = pooler.get_pool(cr.dbname)
    attachment_obj = pool.get('ir.attachment')
    document_data = pool.get('dm.offer.document').browse(cr,uid,document_data)
    if report_type == 'html2html' and document_data.content:
        "Check if to use the internal editor report"
        if not document_data.content:
                return "no_report_for_document"
        report_data = internal_html_report + tools.ustr(document_data.content )+ u"</BODY></HTML>"
        context['doc_type'] = 'email_doc'
        report_data = merge_message(cr, uid, report_data, context)
        if re.search('!!!Missing-Plugin-in DTP document!!!',report_data,re.IGNORECASE) :
            return 'plugin_missing'
        if re.search('!!!Missing-Plugin-Value!!!',report_data,re.IGNORECASE) :
            return 'plugin_error'
        if camp_doc :
           attach_vals={'name' : document_data.name + "_" + str(context['address_id']),
                       'datas_fname' : 'report_test' + report_type ,
                       'res_model' : 'dm.campaign.document',
                       'res_id' : camp_doc,
                       'datas': base64.encodestring(report_data),
                       'file_type':'html'
                       }
           attach_id = attachment_obj.create(cr,uid,attach_vals)
           return 'doc_done'
        return [report_data]
    else:
        return 'wrong_report_type'# }}}

def generate_openoffice_reports(cr, uid, report_type, 
                                document_data, camp_doc, context): # {{{
    " Generate documents created by OpenOffice "

    """ Get reports to process """
    report_content = []
    pool = pooler.get_pool(cr.dbname)    
    attachment_obj = pool.get('ir.attachment')
    document_data = pool.get('dm.offer.document').browse(cr,uid,document_data)    
    report_xml = pool.get('ir.actions.report.xml')
    report_ids = report_xml.search(cr, uid, 
                    [('document_id', '=', document_data.id), 
                    ('report_type', '=', report_type),])
    if not report_ids:
        return "no_report_for_document"
    for report in pool.get('ir.actions.report.xml').browse(cr, uid, report_ids):
        srv = netsvc.LocalService('report.' + report.report_name)
        report_data, report_type = srv.create(cr, uid, [], {}, context)
        if re.search('!!!Missing-Plugin-in DTP document!!!', report_data, re.IGNORECASE):
            return 'plugin_missing' 
        if re.search('!!!Missing-Plugin-Value!!!', report_data, re.IGNORECASE):
            return 'plugin_error'
        if camp_doc: 
            attach_vals = {
                    'name': document_data.name + "_" + str(context['address_id']) + str(report.id),
                    'datas_fname': 'report.' + report.report_name + '.' + report_type,
                    'res_model': 'dm.campaign.document',
                    'res_id': camp_doc,
                    'datas': base64.encodestring(report_data),
                    'file_type': report_type
                    }
            attach_id = attachment_obj.create(cr, uid, attach_vals,
                                                {'not_index_context': True})
        else:
            report_content.append(report_data)
    if report_content and not camp_doc:
        return report_content
    else :
        return 'doc_done' # }}}
        
# TODO : to get sale order id in campign_document
#def get_so(cr,uid,wi_id) :
#    return False

def get_address_id(cr,uid,source,s_id):
    if source == 'address_id' : 
        return getattr(obj, obj.source).id
    else : return False

def precheck(cr, uid, obj, context):	# {{{
    pool = pooler.get_pool(cr.dbname)
    """ Set addess_id depending of the source: partner address, crm case, etc """
    address_id = getattr(obj, obj.source).id
    if not address_id:    
        return {'code': "no_address_for_wi"}

    if obj.step_id:
        step_id = obj.step_id.id
    else:
        return {'code': "no_step_for_wi"}

    camp_mail_service_obj = pool.get('dm.campaign.mail_service')

    """ Set mail service to use """
    if obj.mail_service_id:
        mail_service = obj.mail_service_id
    else:
        if obj.segment_id:
            if not obj.segment_id.proposition_id:
                return {'code': "no_proposition_for_wi"}
            elif not obj.segment_id.proposition_id.camp_id:
                return {'code': "no_campaign_for_wi"}
            else:
                camp_id = obj.segment_id.proposition_id.camp_id.id
                camp_mail_service_id = camp_mail_service_obj.search(cr, uid, 
                                        [('campaign_id', '=', camp_id), 
                                         ('offer_step_id', '=', step_id)])
                if not camp_mail_service_id:
                    return {'code': "no_mail_service_for_campaign"}
                else:
                    mail_service = camp_mail_service_obj.browse(cr, uid, 
                                        camp_mail_service_id)[0].mail_service_id
        else:
            return {'code': "no_segment_for_wi"}

    """ Get offer step documents to process """
    dm_doc_obj = pool.get('dm.offer.document') 
    title = pool.get('res.partner.address').browse(cr, uid, address_id).title
    title_id = pool.get('res.partner.title').search(cr, uid, [('shortcut','=',title)])
    if not title_id :
        return {'code': "no_title_for_customer"}
    gender_id = pool.get('res.partner.title').browse(cr, uid, title_id[0]).gender_id.id
    document_ids = dm_doc_obj.search(cr, uid, [('step_id', '=', obj.step_id.id),
                        ('category_id', '=', 'Production'),
                        ('state','=','validate'),
                        ('lang_id', '=', obj.segment_id.proposition_id.camp_id.lang_id.id),
                        ('gender_id','in',[False,gender_id])
                        ])
    if not document_ids:
        return {'code': "no_document_for_step"}
            
    # TO IMPROVE : Should process all the documents found
    document_data = dm_doc_obj.browse(cr, uid, document_ids[0])
    return (mail_service, document_data, address_id)

def process_report(cr, uid, obj, report_type, mail_service, document_data, address_id, context):
    pool = pooler.get_pool(cr.dbname)
    report_xml = pool.get('ir.actions.report.xml')
    # TODO : Need to process reports of all document  - before that need to change dm_engine
    if not document_data.content and document_data.editor == 'internal':
        return {'code': "no_report_for_document"}
    report_ids = report_xml.search(cr, uid, 
                                   [('document_id', '=', document_data.id), 
                                    ('report_type', '=', report_type),])
    if not report_ids and document_data.editor == 'oord':
        return {'code': "no_report_for_document"}
    r_type = report_type
    if report_type == 'html2html':
        r_type = 'html'

    type_id = pool.get('dm.campaign.document.type').search(cr, uid, [('code', '=', r_type)])
    res = 'doc_done'
    """ Create campaign document """
    vals={
        'workitem_id': obj.id,
        'segment_id': obj.segment_id.id or False,
        'name': obj.step_id.code + "_" + str(address_id),
        'type_id': type_id[0],
        'mail_service_id': mail_service.id,
        'document_id': document_data.id,
        (obj.source): address_id,
        }

    camp_doc = pool.get('dm.campaign.document').create(cr, uid, vals)

    """ If DMS stored document """
    if mail_service.store_document:
        context['address_id'] = address_id
        context['document_id'] = document_data.id
        context['store_document'] = True
        context['workitem_id'] = obj.id
        context['step_id'] = obj.step_id.id
        context['segment_id'] = obj.segment_id.id

        if not 'camp_doc_id' in context : 
            context['camp_doc_id'] = camp_doc
        if not 'workitem_id' in context :
            context['workitem_id'] = obj.id
        if document_data.editor == 'internal':
            res = generate_internal_reports(cr, uid, report_type, 
                                        document_data.id, camp_doc, context)
        elif document_data.editor == 'oord':
            res = generate_openoffice_reports(cr, uid, report_type, 
                                        document_data.id, camp_doc, context)
    return {'code':res, 'model':'dm.campaign.document', 'ids':[camp_doc]} # }}}

def document_process(cr, uid, obj, report_type, context): # {{{
    result = precheck(cr, uid, obj, context)
    if type(result) == type({}):
        return result
    else:
        mail_service, document_data, address_id = result
        result = process_report(cr, uid, obj, report_type, mail_service, document_data, address_id, context)
    return result#}}}
	
"""
def compute_customer_plugin(cr, uid, **args): # {{{
    res  = pool.get('ir.model').browse(cr, uid, args['plugin_obj'].model_id.id)    
    args['model_name'] = res.model
    args['field_name'] = str(args['plugin_obj'].field_id.name)
    args['field_type'] = str(args['plugin_obj'].field_id.ttype)
    args['field_relation'] = str(args['plugin_obj'].field_id.relation)
    return customer_function(cr, uid, **args) # }}}
"""
def _generate_value(cr, uid, plugin_obj, **args): # {{{
    pool = pooler.get_pool(cr.dbname)
    localcontext = {'cr': cr,'uid': uid, 'plugin_obj' : plugin_obj}
    localcontext.update(args)

    plugin_args = {}
    plugin_value = ''
    if plugin_obj.type in ('fields','image'):
        res  = pool.get('ir.model').browse(cr, uid, plugin_obj.model_id.id)    
        args['model_name'] = res.model
        args['field_name'] = str(plugin_obj.field_id.name)
        args['field_type'] = str(plugin_obj.field_id.ttype)
        args['field_relation'] = str(plugin_obj.field_id.relation)
        plugin_value = customer_function(cr, uid, **args)
    else:
        arg_ids = pool.get('dm.plugin.argument').search(cr, uid, 
                                            [('plugin_id', '=', plugin_obj.id)])
        for arg in pool.get('dm.plugin.argument').browse(cr, uid, arg_ids):
            if not arg.stored_plugin:
                plugin_args[str(arg.name)] = tools.ustr(arg.value)
            else:
                plugin_args[str(arg.name)] = tools.ustr(_generate_value(cr, uid, 
                                    arg.custome_plugin_id, **args))
        if plugin_obj.type == 'dynamic' and plugin_obj.python_code:
            localcontext.update(plugin_args)
            localcontext['pool'] = pool
            exec plugin_obj.python_code.replace('\r','') in localcontext
            plugin_value = plugin_obj.code in localcontext and \
                                        localcontext[plugin_obj.code] or ''
        elif plugin_obj.type == 'dynamic_text':
            plugin_args['ref_text_id'] = plugin_obj.ref_text_id.id
            args.update(plugin_args)
            plugin_value = dynamic_text(cr, uid, **args)
        elif plugin_obj.type == 'url':
            plugin_args['encode'] = plugin_obj.encode
            plugin_value = php_url(cr, uid, **plugin_args)
        else:
            path = os.path.join(os.getcwd(), "addons/dm/dm_dtp_plugins",cr.dbname)
            plugin_name = plugin_obj.file_fname.split('.')[0]
            sys.path.append(path)
            X =  __import__(plugin_name)
            plugin_func = getattr(X, plugin_name)
            plugin_value = plugin_func(cr, uid, **args)
    plugin_value = plugin_value and plugin_value or (plugin_obj.err_notify and '!!!Missing-Plugin-Value!!!' or '')
    return plugin_value # }}}

def generate_plugin_value(cr, uid, **args): # {{{
    if not 'document_id' in args and not args['document_id']:
        return False
    vals = {}
    pool = pooler.get_pool(cr.dbname)
    dm_document = pool.get('dm.offer.document')
    dm_plugins_value = pool.get('dm.plugins.value')
    
    plugins = dm_document.browse(cr, uid, args['document_id'] )
    doc_plugin_ids = map(lambda x: x.id,plugins.document_template_plugin_ids)
    if 'plugin_list' in args and args['plugin_list'] :
        "Get plugins to compute value"
        p_ids = pool.get('dm.dtp.plugin').search(cr, uid, [('code', 'in', args['plugin_list'])])
    else :
        "If no plugins in document do nothing"
        return {}
    for plugin_obj in pool.get('dm.dtp.plugin').browse(cr, uid, p_ids) :
        if plugin_obj.id not in doc_plugin_ids:
            plugin_value = '!!!Missing-Plugin-in DTP document!!!'
        else :
            "Compute plugin value"
            plugin_value = _generate_value(cr, uid, plugin_obj, **args)
#       dnt remove this comment it s for url changes
#        if plugin_obj.type == 'url':
#            vals['%s_text_display'%str(plugin_obj.code)] = plugin_value[-1]
#            plugin_value = plugin_value[0]
        if plugin_obj.store_value:
            if not 'camp_doc_id' in args and not args['camp_doc_id']:
                return False
            dm_plugins_value.create(cr, uid, {
                'document_id': args['camp_doc_id'],
                'plugin_id': plugin_obj.id,
                'value': plugin_value
            })
        vals[str(plugin_obj.code)] = plugin_value
    return vals # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
