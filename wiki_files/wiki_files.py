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
import difflib
from ftplib import FTP

import base64, urllib

class wiki_media(osv.osv):
    """Wiki media"""
    _name = "wiki.media"
    _description = "Wiki Media"
    _rec_name = "file"

    def _wiki_tag(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}

        images = ['jpg','gif','png']

        for file_wiki in self.browse(cr, uid, ids, context=context):
            filename = file_wiki.file
            if filename[-3:] in images:
                result = 'img:%s' % (filename)
            else:
                result = '[%s]' % (filename)

            res[file_wiki.id] = result
        return res

    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['file'])
        images = ['jpg','gif','png']
        if each['file'][-3:] in images:
            try:
                (filename, header) = urllib.urlretrieve(each['file'])
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
            except:
                img = ''
        else:
            img = each['file']
        return img
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res

    _columns = {
        'file': fields.char('File', size=128, required=True, readonly=True),
        'media_id': fields.many2one('wiki.wiki', 'Wiki Name'),
        'file_wiki': fields.function(_wiki_tag, string='File', method=True, type='char', size=256),
        'preview':fields.function(_get_image, type="binary", method=True),
    }

wiki_media()

class wiki_wiki(osv.osv):
    """Wiki Page"""
    _inherit = "wiki.wiki"

    _columns = {
        'media_ids': fields.one2many('wiki.media', 'media_id', 'Media File'),
    }

wiki_wiki()

class wiki_files_conf(osv.osv):
    """Wiki files Configuration"""
    _name = "wiki.files.conf"
    _description = "Wiki Files Conf"
    
    _columns = {
        'name': fields.char('FTP Server Name', size=64, select=True, required=True),
        'active': fields.boolean('Active', help='If the Active field is not set, the FTP server will be hide without removing it.'),
        'ftpip': fields.char('IP', size=256),
        'ftpdirectory': fields.char('Directory', size=256, help='If you use a directory, insert the path of the FTP folder, otherwise insert a dot ".".'),
        'ftpusername': fields.char('Username', size=32, help='The login user to connect to the ftp server.'),
        'ftppassword': fields.char('Password', size=32, help='The login password to conect to the ftp server.'),
        'ftpurl': fields.char('URL', size=256, help='URL FTP Dir: "http://domain/directory/".'),
    }

    _sql_constraints = [
        ('active_uniq', 'unique (active)', 'Active must be unique.')
    ]

    _defaults = {
        'active' : 'True',
    }

    def check_ftp(self, cr, uid, ids, context):
        if context is None:
            context = {}

        for id in ids:
            wiki_file = self.browse(cr, uid, id)

            try: ftp = FTP(wiki_file.ftpip)
            except:
                raise osv.except_osv(_('Error !'), _("IP FTP connection was not successfully!"))

            try: ftp.login(wiki_file.ftpusername, wiki_file.ftppassword)
            except:
                raise osv.except_osv(_('Error !'), _("Username/password FTP connection was not successfully!"))

            ftp.quit()
            raise osv.except_osv(_('Ok !'), _("FTP connection was successfully!"))

wiki_files_conf()
