# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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

import os
import base64

from osv import fields, osv
from tools.translate import _

class LoadProductMedia(osv.osv_memory):
    """Load Product Medias"""
    _name = "load.product.media"
    _description = __doc__
    _columns = {
        'media': fields.binary('Image'),
        'media_fname': fields.char('Filename', size=64),
    }

    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        if not os.path.exists(path):
            raise osv.except_osv(_('Error!'), _('The path to OpenERP medias folder does not exists on the server !'))        
        
        full_path = os.path.join(path, filename)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True

    def _update_image(self, cr, uid, data, context):
        self.pool.get('product.images').write(cr,
                                              uid,
                                              context['active_id'],
                                              data,
                                              context)
        return True

    def _create_image(self, cr, uid, data, context):
        self.pool.get('product.images').create(cr,
                                               uid,
                                               data,
                                               context)
        return True

    def load_media(self, cr, uid, data, context=None):
        """Load and create a product image """
        if context == None:
            raise osv.except_osv(_('Error!'), _('Context is missing !'))

        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        if not company.local_media_repository:
            raise osv.except_osv(_('Error!'), _('The path to OpenERP medias folder is not configured on the company !'))

        media = self.browse(cr, uid, data[0], context).media or False
        if not media:
            raise osv.except_osv(_('Error!'), _('No media selected !'))
        filename = self.browse(cr, uid, data[0], context).media_fname or False
        if not filename:
            raise osv.except_osv(_('Error!'), _('No filename !'))

        self._save_file(company.local_media_repository, filename, media)

        data = {'filename': filename,
                'link': True,}
        if context['create']:
            data.update({'name': filename,
                         'product_id': context['product_id']})
            self._create_image(cr, uid, data, context)
        else:
            self._update_image(cr, uid, data, context)

        return {'type':'ir.actions.act_window_close'}

LoadProductMedia()

