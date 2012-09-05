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

from osv import fields
from osv import osv
import pooler
import re
import base64
pattern = re.compile("/Count\s+(\d+)")

from dm.dm_report_design import generate_internal_reports, generate_openoffice_reports

class dm_campaign_document_job_sorting_rule(osv.osv): # {{{
    _name = "dm.campaign.document.job.sorting_rule"
    
    _columns = {
        'name': fields.char('Name', required=True, size=64), 
        'code': fields.char('Code', required=True, size=64),
        'by_customer_country': fields.boolean('By Customer Country'),
        'by_product': fields.boolean('Group By Product'),
        'by_page_qty': fields.boolean('Group By Page Quantity'),
        'by_offer_step': fields.boolean('Group By Offer Step'),
        'by_trademark': fields.boolean('Group By Trademark'),
        'by_dealer': fields.boolean('Group By Dealer'),
        'qty_limit': fields.integer('Group Qty. limit')
    }
    
dm_campaign_document_job_sorting_rule() # }}}

class dm_campaign_document_job_batch(osv.osv): # {{{
    _name = "dm.campaign.document.job.batch"

    _columns = {
        'name': fields.char('Name', required=True, size=64),
        'campaign_document_job_ids': fields.one2many('dm.campaign.document.job', 'batch_id', 'Campaign Document Jobs'),
        'state': fields.selection([('pending', 'Pending'), ('error', 'Error'), ('done', 'Done')], 'State'),
    }
    _defaults = {
        'state': lambda *a: 'pending',
        }
    
dm_campaign_document_job_batch() # }}}

class dm_campaign_document_job(osv.osv): # {{{
    _name = "dm.campaign.document.job"

    _columns = {
        'name': fields.char('Name', required=True, size=64),
        'batch_id': fields.many2one('dm.campaign.document.job.batch', 'Job Batch'),
        'campaign_document_ids': fields.one2many('dm.campaign.document', 'campaign_document_job', 'Campaign Documents'),
        'process_date': fields.datetime('Processing Date'),
        'state': fields.selection([('pending', 'Pending'), ('error', 'Error'), ('done', 'Done')], 'State'),
        'sorting_rule_id': fields.many2one('dm.campaign.document.job.sorting_rule', 'Sorting Rule'),
        'sorting_name' : fields.char('Sorting value', size = 64),
        'use_front_recap': fields.boolean('Use Front Job Recap'),
        'use_bottom_recap': fields.boolean('Use Bottom Job Recap'),        
    }
    _defaults = {
        'state': lambda *a: 'pending',
        }    
dm_campaign_document_job() # }}}

class dm_printer_model(osv.osv): # {{{
    _name = "dm.printer.model"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'note': fields.text('Description'),

        }
dm_printer_model() # }}}

class dm_printer_tray_model(osv.osv): # {{{
    _name = "dm.printer_tray.model"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'note': fields.text('Description'),

        }
dm_printer_tray_model() # }}}

class dm_printer(osv.osv): # {{{
    _name = "dm.printer"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'printer_model_id': fields.many2one('dm.printer.model','Printer Model'),
        'mail_service_id': fields.many2one('dm.mail_service','Mail Service'),
        'note': fields.text('Description'),

        }
dm_printer() # }}}

class dm_printer_tray(osv.osv): # {{{
    _name = "dm.printer_tray"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'printer_tray_model_id' : fields.many2one('dm.printer_tray.model','Printer Tray Model'),
        'printer_id' : fields.many2one('dm.printer','Printer'),
        'note': fields.text('Description'),

        }
dm_printer_tray() # }}}        

class dm_offer_document(osv.osv): # {{{
    _inherit = "dm.offer.document"
    
    _columns = {
        'printer_tray_model_id':fields.many2one('dm.printer_tray.model','Document Type'),
        'verso': fields.boolean('Verso'),
        'sequence': fields.integer('Sequence')
    }
    
dm_offer_document() # }}}

class dm_mail_service(osv.osv): # {{{
    _inherit = "dm.mail_service"
    
    _columns = {
          'default_printer_id': fields.many2one('dm.printer', 'Default Printer'),
          'default_printer_tray_id': fields.many2one('dm.printer_tray','Default Printer Tray'),
          'sorting_rule_id': fields.many2one('dm.campaign.document.job.sorting_rule', 'Sorting Rule'),
          'front_job_recap': fields.many2one('dm.offer.document', 'Front Job Recap'),
          'bottom_job_recap': fields.many2one('dm.offer.document', 'Bottom Job Recap'),
          'user_id': fields.many2one('res.users', 'Printer User'),
        }
    
dm_mail_service() # }}}

class dm_campaign_document(osv.osv): # {{{
    _inherit = 'dm.campaign.document'
    
    _columns = {
        'printer_id': fields.many2one('dm.printer','Printer'),
        'printer_tray_id': fields.many2one('dm.printer_tray','Printer Tray'),
        'campaign_document_job': fields.many2one('dm.campaign.document.job', 'Campaign Document Job'),
        'campaign_document_job_position': fields.integer('Campaign Document Job Position'),
        'verso': fields.boolean('Verso')
    }
    
dm_campaign_document() # }}}

def generate_document_job(cr, uid, obj_id, context):
    pool = pooler.get_pool(cr.dbname)
    camp_doc_object = pool.get('dm.campaign.document')
    camp_doc = camp_doc_object.browse(cr,uid,obj_id)
    ms_id = camp_doc.mail_service_id
    type_id = pool.get('dm.campaign.document.type').search(cr, uid, [('code', '=', 'pdf')])
    type_id = type_id and type_id[0] or ''
    sorting_name = ''
    offer_doc_obj = pool.get('dm.offer.document').browse(cr,uid,camp_doc.document_id.id)
    printer_tray_id = ''
    
    if offer_doc_obj.printer_tray_model_id:
        printer_tray_id = pool.get('dm.printer_tray').search(cr, 
                    uid,
                    [('printer_tray_model_id','=',offer_doc_obj.printer_tray_model_id.id)])
        if printer_tray_id :
            printer_tray_id = printer_tray_id[0]
            printer_tray_obj = pool.get('dm.printer_tray').browse(cr, uid, printer_tray_id) 
            printer_id = printer_tray_obj.printer_id.id
    if not printer_tray_id:
        printer_tray_id = ms_id.default_printer_tray_id.id
        printer_id = ms_id.default_printer_id.id
        
    camp_doc_object.write(cr, uid, [obj_id], {'printer_tray_id': printer_tray_id,
                                              'printer_id': printer_id})
    
    if ms_id.sorting_rule_id.by_customer_country:
	    sorting_name = str(camp_doc.address_id.country_id.id)
    if ms_id.sorting_rule_id.by_offer_step:
        v = str(camp_doc.document_id.step_id.id)
        sorting_name = sorting_name and sorting_name+'_'+v or v        
    if ms_id.sorting_rule_id.by_page_qty:
        attach_obj = pool.get('ir.attachment')
        pattern = re.compile(r"/Count\s+(\d+)")
        attach_id = attach_obj.search(cr, uid,[('res_id', '=', camp_doc.id), 
	                           ('res_model', '=', 'dm.campaign.document')])
        if attach_id:
            attach = attach_obj.browse(cr, uid, attach_id[0])
            datas = base64.decodestring(attach.datas)
            v = str(pattern.findall(datas) and pattern.findall(datas)[0] or 0)
            sorting_name = sorting_name and sorting_name+'_'+v or v
    if ms_id.sorting_rule_id.by_product:
        if 'workitem_id' in context:
            res = pool.get('dm.workitem').browse(cr,uid,context['workitem_id'])
            if res.sale_order_id:
                product =['%d:%s'%(line.product_id.id,line.product_uom_qty) for line in res.sale_order_id.order_line]
                product.sort()
                v = '_'.join(product)
                sorting_name = sorting_name and sorting_name+'_'+v or v
    if ms_id.sorting_rule_id.by_trademark:
        if 'segment_id' in context:
            res = pool.get('dm.campaign.proposition.segment').browse(cr,uid,context['segment_id'])
            if res.campaign_id and res.campaign_id.trademark_id:
                v = str(res.campaign_id.trademark_id.id)
                sorting_name = sorting_name and sorting_name+'_'+v or v
    if ms_id.sorting_rule_id.by_dealer:
        if 'segment_id' in context:
            res = pool.get('dm.campaign.proposition.segment').browse(cr,uid,context['segment_id'])
            if res.campaign_id and res.campaign_id.dealer_id:
                v = str(res.campaign_id.dealer_id.id)
                sorting_name = sorting_name and sorting_name+'_'+v or v
    if sorting_name:
        camp_doc_job_obj = pool.get('dm.campaign.document.job')
        job_ids = camp_doc_job_obj.search(cr, uid, [('state', '=', 'pending'),('sorting_rule_id', '=', ms_id.sorting_rule_id.id),('sorting_name','=',sorting_name)])
        job_id = ''
        for j_id in camp_doc_job_obj.browse(cr, uid, job_ids):
            if not ms_id.sorting_rule_id.qty_limit or ms_id.sorting_rule_id.qty_limit ==0 :
                job_id = j_id.id
            elif len(j_id.campaign_document_ids) < ms_id.sorting_rule_id.qty_limit:
                job_id = j_id.id
        if not job_id :
            job_vals = {
                    'name': (camp_doc.segment_id and camp_doc.segment_id.name or '') + str(sorting_name),
	             	'user_id': ms_id.user_id.id,
		            'sorting_rule_id': ms_id.sorting_rule_id.id,
                    'sorting_name': sorting_name,
                    'use_front_recap': ms_id.front_job_recap and True or False,
                    'bottom_job_recap': ms_id.bottom_job_recap and True or False,
                    'campaign_document_ids': [[4,obj_id]],
                    }
            job_id = camp_doc_job_obj.create(cr,uid,job_vals)
            if  ms_id.front_job_recap or ms_id.bottom_job_recap:
                camp_vals={
                       'segment_id': camp_doc.segment_id.id or False,
                       'name': camp_doc.document_id.step_id.code + "_" + str(camp_doc.address_id.id),
                       'type_id': type_id,
                       'mail_service_id': ms_id.id,
                       'address_id': camp_doc.address_id.id,
                       'campaign_document_job': job_id,
                       'printer_tray_id': printer_tray_id,
                       'printer_id': printer_id,
                  }
                if not 'address_id' in context :
                    context['address_id'] = camp_doc.address_id.id
                if not 'document_id' in context :
                    context['document_id'] = camp_doc.document_id.id
                if not 'store_document' in context :
                    context['store_document'] = ms_id.store_document
                if not 'workitem_id' in context :
                    context['workitem_id'] = camp_doc.workitem_id.id
                if not 'step_id' in context :
                    context['step_id'] = camp_doc.workitem_id.step_id.id
                if not 'segment_id' in context :
                    context['segment_id'] = camp_doc.workitem_id.segment_id.id             
                # reports for the front and bottom job should be saved as 
                # attachment of the campaign document    ?
                if ms_id.front_job_recap: 
                    camp_vals['document_id'] = ms_id.front_job_recap.id
                    new_camp_id = camp_doc_object.create(cr,uid,camp_vals)
                    report_data = generate_openoffice_reports(cr, uid, 'pdf', ms_id.front_job_recap.id, new_camp_id, context)
                    ms_status = pool.get('dm.workitem')._check_sysmsg(cr, uid, report_data, context)
                    camp_doc_object.write(cr, uid, [new_camp_id],
                        {'state': ms_status['state'],
                        'error_msg': ms_status['msg'],})
                        
                if ms_id.bottom_job_recap:
                    camp_vals['document_id'] = ms_id.bottom_job_recap.id
                    new_camp_id = camp_doc_object.create(cr,uid,camp_vals)
                    report_data = generate_openoffice_reports(cr, uid, 'pdf', ms_id.bottom_job_recap.id, new_camp_id, context)
                    ms_status = pool.get('dm.workitem')._check_sysmsg(cr, uid, report_data, context)
                    camp_doc_object.write(cr, uid, [new_camp_id],
                        {'state': ms_status['state'],
                        'error_msg': ms_status['msg'],})
                        
        else:
          camp_doc_job_obj.write(cr, uid, job_id, 
                                       {'campaign_document_ids': [[4,obj_id]]})
    return {'code':'doc_done','ids': camp_doc.id}		

	
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
