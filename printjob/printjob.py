# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Ferran Pegueroles <ferran@pegueroles.com>
# Copyright (c) 2009 Albert Cervera i Areny <albert@nan-tic.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import tools
import time 
import datetime 
from osv import fields,osv

import base64, os, string
from tempfile import mkstemp
import netsvc
import pooler, ir, tools
from service import security

import threading, thread
import time
import base64
import addons
from tools.translate import _

#
#  Printers
#
class printjob_printer(osv.osv):
    _name = "printjob.printer"
    _description = "Printer"

    _columns = {
        'name' : fields.char('Name',size=64,required=True,select="1"),
        'system_name': fields.char('System Name',size=64,required=True,select="1"),
        'default':fields.boolean('Default Printer',required=True,readonly=True),
    }
    _order = "name"
    
    _defaults = {
        'default': lambda *a: False,
    }

    def set_default(self, cr, uid, ids, context):
        if not ids:
            return
        default_ids= self.search(cr, uid,[('default','=',True)])
        self.write(cr, uid, default_ids, {'default':False}, context)
        self.write(cr, uid, ids[0], {'default':True}, context)
        return True
    
    def get_default(self,cr,uid,context):
        printer_ids = self.search(cr, uid,[('default','=',True)])
        if printer_ids:
            return printer_ids[0]
        return None

printjob_printer()



#
# Actions
#

def _available_action_types(self, cr, uid, context={}):
    return [
        ('spool',_('Send to Spool Only')),
        ('server',_('Send to Printer')),
        ('client',_('Send to Client')),
        ('user_default',_("Use user's defaults")),
    ]

class printjob_action(osv.osv):
    _name = 'printjob.action'
    _description = 'Print Job Action'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'type': fields.selection(_available_action_types, 'Type', required=True),
    }
printjob_action()

# 
# Users
#

class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"

    def _user_available_action_types(self, cr, uid, context={}):
        return [x for x in _available_action_types(self, cr, uid, context) if x[0] != 'user_default']

    _columns = {
        'printjob_action': fields.selection(_user_available_action_types, 'Printing Action'),
        'printjob_printer_id': fields.many2one('printjob.printer', 'Default Printer'),
    }

res_users()

# 
#  Printjobs
#
import re
rxcountpages=re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)

class printjob_job(osv.osv):
    _name = "printjob.job"
    _description = "Print Job"

    def _doc_pages(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for d in self.browse(cr, uid, ids):
            if d.result:
                data = base64.decodestring(d.result)
                res[d.id] = len(rxcountpages.findall(data))
            else:
                res[d.id] = 0
        return res

    _columns = {
        'name' : fields.char('Name',size=64,required=True,select="1"),
        'format' : fields.char('Format',size=64,readonly=True),
        'state': fields.selection([('draft','In Progress'),
                                ('ready','Processed'), 
                                ('error','Error'), 
                                ('done','Done')], 'State', required=True, select="1"),
        'report' : fields.char('Report',size=256,required=True,select="1"),
        'result': fields.text('Document',readonly=True),
        'ids': fields.text('Ids'),
        'data': fields.text('Param. Data'),
        'context': fields.text('Context Data'),
        'action': fields.selection(_available_action_types, 'Action', required=True, readonly=True),
        'keep':fields.boolean('Keep the document',help="A job marked with keep will not be deleted by the cron job"),
        'pages': fields.function(_doc_pages, method=True, string='Number of Pages', type='integer'),


        'create_date': fields.datetime('Created' ,readonly=True),
        'create_uid': fields.many2one('res.users', 'Created By',readonly=True),
    }
    _order = "id desc"
    
    _defaults = {
        'state': lambda *a: 'draft',
        'keep': lambda *a: False,
        'action':lambda *a : 'spool'
    }

    def _clean_old(self, cr, uid, ids=False, context={}):
        """
          Function called by the cron to delete old entries
        """
        limit = datetime.datetime.now() - datetime.timedelta(days=2)
        cr.execute('select id from printjob_job \
                where create_date<%s and not keep',
            (limit.strftime('%Y-%m-%d %H:%M:%S'),))
        ids2 = map(lambda x: x[0], cr.fetchall() or [])
        if ids2:
            logger = netsvc.Logger()
            logger.notifyChannel("report", netsvc.LOG_INFO,
                 "Deleted old completed reports '%s'." % str(ids2))
            self.unlink(cr, uid, ids2, context)
        return True

    def print_direct(self, cr, uid, id, printer, context):
        logger = netsvc.Logger()

        job = self.browse(cr, uid, id, context)

        fd, file_name = mkstemp()
        os.write(fd, base64.decodestring(job.result))
        if job.format == 'raw':
            # -l is the same as -o raw
            cmd = "lpr -l -P %s %s" % (printer,file_name)
        else:
            cmd = "lpr -P %s %s" % (printer,file_name)
        print "PRINTING: ", cmd
        logger.notifyChannel("report", netsvc.LOG_INFO,"Printing job : '%s'" % cmd)
        os.system(cmd)

printjob_job()

    

class report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'property_printjob_action': fields.property(
            #'ir.actions.report.xml',
            'printjob.action',
            type='many2one',
            relation='printjob.action',
            string='Action',
            view_load=True,
            method=True,
        ),
        'printjob_printer_id': fields.many2one('printjob.printer', 'Printer'),
        'printjob_action_ids': fields.one2many('printjob.report.xml.action', 'report_id', 'Actions', help='This field allows configuring action and printer on a per user basis'),
    }

    def behaviour(self, cr, uid, ids, context={}):
        result = {}

        # Set hardcoded default action
        default_action = 'client'
        # Retrieve system wide printer
        default_printer = self.pool.get('printjob.printer').get_default(cr,uid,context)
        if default_printer:
            default_printer = self.pool.get('printjob.printer').browse(cr,uid,default_printer,context).system_name


        # Retrieve user default values
        user = self.pool.get('res.users').browse(cr, uid, context)
        if user.printjob_action:
            default_action = user.printjob_action
        if user.printjob_printer_id:
            default_printer = user.printjob_printer_id.system_name

        for report in self.browse(cr, uid, ids, context):
            action = default_action
            printer = default_printer

            # Retrieve report default values
            if report.property_printjob_action and report.property_printjob_action.type != 'user_default':
                action = report.property_printjob_action.type
            if report.printjob_printer_id:
                printer = report.printjob_printer_id.system_name

            # Retrieve report-user specific values
            user_action = self.pool.get('printjob.report.xml.action').behaviour(cr, uid, report.id, context)
            if user_action and user_action['action'] != 'user_default':
                action = user_action['action']
                if user_action['printer']:
                    printer = user_action['printer']

            result[report.id] = {
                'action': action,
                'printer': printer,
            }
        return result


report_xml()

class report_xml_action(osv.osv):
    _name = 'printjob.report.xml.action'
    _description = 'Report Printing Actions'
    _columns = {
        'report_id': fields.many2one('ir.actions.report.xml', 'Report', required=True, ondelete='cascade'),
        'user_id': fields.many2one('res.users', 'User', required=True, ondelete='cascade'),
        'action': fields.selection(_available_action_types, 'Action', required=True),
        'printer_id': fields.many2one('printjob.printer', 'Printer'),
    }

    def behaviour(self, cr, uid, report_id, context={}):
        result = {}
        ids = self.search(cr, uid, [('report_id','=',report_id),('user_id','=',uid)], context=context)
        if not ids:
            return False
        action = self.browse(cr, uid, ids[0], context)
        return {
            'action': action.action,
            'printer': action.printer_id.system_name,
        }
report_xml_action()


class except_print(Exception):
    def __init__(self, name, value, exc_type='warning'):
        self.name = name
        self.exc_type = exc_type
        self.value = value
        self.args = (exc_type, name)
        self.message = "\n".join([" -- ".join( (exc_type , name ) ) , '' , value])

class report_spool(netsvc.Service):
    def __init__(self, name='report'):
        netsvc.Service.__init__(self, name)
        self.joinGroup('web-services')
        self.exportMethod(self.report)
        self.exportMethod(self.report_get)
        self._reports = {}
        self.id = 0
        self.id_protect = threading.Semaphore()

    def report(self, db, uid, passwd, object, ids, datas=None, context=None):

        logger = netsvc.Logger()
        if not datas:
            datas={}
        if not context:
            context={}

        security.check(db, uid, passwd)
        logger.notifyChannel("report", netsvc.LOG_INFO,"request report '%s'" % str(object))
        # Reprint a printed job
        if object == 'printjob.reprint':
            return ids[0]

        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(cr.dbname)
        
        # First of all load report defaults: name, action and printer
        report_obj = pool.get('ir.actions.report.xml')
        report = report_obj.search(cr,uid,[('report_name','=',object)])
        if report:
            report = report_obj.browse(cr,uid,report[0])
            name = report.name
            data = report.behaviour()[report.id]
            action = data['action']
            printer = data['printer']
        else:
            name = object
            action = 'spool'
            printer = False

        # Detect if defaults are being overriden for this report call
        batch = False
        if 'print_batch' in context:
            batch = context['print_batch']
        if 'print_batch' in datas:
            batch = datas['print_batch']
        if 'form' in datas:
            if 'print_batch' in datas['form']:
                batch = datas['form']['print_batch']

        if batch:
            action = 'server'
            # Search default printer
            printer_id = False
            if 'printer' in context:
                printer_id = context['printer']
            if 'printer' in datas:
                printer_id = datas['printer']
            if 'form' in datas:
                if 'printer' in datas['form']:
                    printer_id = datas['form']['printer']
            printer = False
            if printer_id:
                printer_ids = pool.get('printjob.printer').read(cr, uid, [printer_id],['system_name'])
                if printer_ids:
                    printer = printer_ids[0]['system_name']
            else:
                printer_id = pool.get('printjob.printer').get_default(cr,uid,context)
                if printer_id:
                    printer = pool.get('printjob.printer').browse(cr,uid,printer_id,context).system_name

        # 
        # Create new printjob.job
        #
        job_id = pool.get("printjob.job").create(cr,uid,{
            'name': name,
            'report': object,
            'ids': str(ids),
            'data': str(datas),
            'context': str(context),
            'result': False,
            'action': action,
        }, context)
        cr.commit()
#        cr.close()
    
        def print_thread(id, uid, ids, datas, context, printer):
            logger.notifyChannel("report", netsvc.LOG_DEBUG,
                 "Printing thread started")

            cr = pooler.get_db(db).cursor()
            pool = pooler.get_pool(cr.dbname)

            service = netsvc.LocalService('report.'+object)
            (result, format) = service.create(cr, uid, ids, datas, context)

            pool.get("printjob.job").write( cr, uid, id, {
                'result': base64.encodestring(result),
                'format': format,
                'state': 'ready',
            }, context)

            if printer:
                pool.get('printjob.job').print_direct(cr, uid, id, printer, context)

            cr.commit()
            cr.close()
            return True

        if action != 'server':
            printer = False
        thread.start_new_thread(print_thread, (job_id, uid, ids, datas, context, printer))

        if action == 'spool':
            raise except_print(_('Report generated in background'),
                               _('This report is generated in background. In a few minutes look at your print jobs.'))
        elif action == 'server':
            raise except_print(_('Report sent to printer'),
                                _('This report has been sent directly to printer: %s') % printer )
        return job_id


    def report_get(self, db, uid, passwd, report_id):
        security.check(db, uid, passwd)

        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(cr.dbname)
        report = pool.get('printjob.job').browse(cr, uid, report_id)

        if not report:
            cr.close()
            raise Exception, 'ReportNotFound'

        if report.create_uid.id != uid:
            cr.close()
            raise Exception, 'AccessDenied'
      
        res = {'state': report.state in ('ready','done')}
        if res['state']:
            res['result'] = report.result
            res['format'] = report.format
            if report.state == 'ready':
                pool.get('printjob.job').write(cr,uid,report_id,{
                    'state': 'done',
                })
                cr.commit()
        cr.close()
        return res

report_spool()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
