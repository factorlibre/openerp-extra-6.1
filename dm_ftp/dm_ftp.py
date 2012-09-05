# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import fields
from osv import osv
from ftplib import FTP
from StringIO import StringIO
import pooler
import re
import base64
from dm.dm_document import generate_report

class dm_mail_service(osv.osv): # {{{
    _inherit = "dm.mail_service"
    
    _columns = {
            'ftp_address': fields.char('Address', size=64),
            'ftp_port': fields.integer('Port'),   
            'ftp_dir': fields.char('Directory', size=128,help="Specify full path of the directory"),
            'ftp_user': fields.char('User', size=64),
            'ftp_password': fields.char('Password', size=64),
            'ssh_use': fields.boolean('Use SFTP'),
            'ssh_key': fields.char('SSH Key', size=64),
        }
dm_mail_service() # }}}

def send_ftp_document(cr, uid, obj_id, context):
    pool = pooler.get_pool(cr.dbname)
    obj = pool.get('dm.campaign.document').browse(cr, uid, obj_id)
    ms = obj.mail_service_id
    if not ms.ftp_address:
        return {'code':'ftp_address_missing','ids':[obj.id]}
    try :
        ip = ms.ftp_address #+ ms.ftp_port and (':%d'%ms.ftp_port) or ''
        ftp = FTP(ip)
        if ms.ftp_user:
            ftp.login(ms.ftp_user,ms.ftp_password or '')
        else :
            ftp.login()
        if ms.ftp_dir:
            ftp.cwd(ms.ftp_dir)
    except Exception,e:
        return {'code':'ftp_error','ids':[obj.id], 'err_msg':e}
    message = generate_report(cr, uid, obj.id, 'pdf', 'pdf', context)
    if type(message) == type({}):
        return message
    for i in range(len(message)):
        try :
            print '_'.join([obj.name,str(obj.address_id.id),str(obj.segment_id.id)])
            ftp.storbinary('STOR '+'_'.join([obj.name,str(obj.address_id.id),str(obj.segment_id.id),str(i+1)]),StringIO(message[i]))
        except Exception,e:
            return {'code':'ftp_error','ids':[obj.id], 'err_msg':e}
    ftp.quit()
    return {'code':'ftp_doc_sent','ids':[obj.id]}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
