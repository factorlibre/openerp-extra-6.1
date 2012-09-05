# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


from osv import fields, osv
from tools.translate import _
#import difflib
from ftplib import FTP

import re
import os
import base64, urllib
import unicodedata

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


class wiki_files_wizard(osv.osv_memory):
    """ wiki files """
    _name = "wiki.files.wizard"
    _description = "Wiki Files Wizard"
    
    _columns = {
        'file':fields.binary('File', required=True),
		'filename': fields.char('File Name', size=256, required=True),
        'result': fields.text('Result', readonly=True),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }
    
    _defaults = {
        'state': lambda *a: 'first',
    }

    def publish_image(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        form = self.browse(cr, uid, ids[0])

        wiki_files_conf_id = self.pool.get('wiki.files.conf').search(cr, uid, [('active', '=', 1)])
        if not wiki_files_conf_id:
            raise osv.except_osv(_('Error'),_("Configure your Wiki Files!"))

        wiki_conf = self.pool.get('wiki.files.conf').browse(cr, uid, wiki_files_conf_id[0])

        images = ['jpg','gif','png']

        file_name =  form.filename.split('.')
        if len(file_name) == 0:
            raise osv.except_osv(_('Error'),_("File name don't have extension."))

        filename = slugify(unicode(file_name[0],'UTF-8'))
        filename += "."+file_name[1].lower()

        path = os.path.abspath( os.path.dirname(__file__) )
        path += '/tmp/'

        fileurl = wiki_conf.ftpurl
        if not fileurl[-1] == '/':
            fileurl += '/' 

        b64_file = form.file
        full_path = os.path.join(path, filename)

        #copy local server (tmp dir)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()

        #send ftp server
        ftp = FTP(wiki_conf.ftpip)
        ftp.login(wiki_conf.ftpusername, wiki_conf.ftppassword)
        ftp.cwd(wiki_conf.ftpdirectory)
        f=file(full_path,'rb')
        ftp.storbinary('STOR '+os.path.basename(full_path),f)
        ftp.quit()

        #delete local server (tmp dir)
        try:
            os.remove(full_path)
        except:
            raise osv.except_osv(_('Error'),_("File don't remove local server."))

        for data in data['active_ids']:
            values = {
                'file': fileurl+filename,
                'media_id': data,
            }
            self.pool.get('wiki.media').create(cr, uid, values, context)

        if filename[-3:] in images:
            result = 'img:%s%s' % (fileurl,filename)
        else:
            result = '[%s%s]' % (fileurl,filename)
           
        values = {
            'state':'done',
            'result': result,
        }
        self.write(cr, uid, ids, values)

wiki_files_wizard()
