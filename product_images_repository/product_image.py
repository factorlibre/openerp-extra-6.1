# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi & Guewen Baconnier. Copyright Camptocamp SA
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
import base64, urllib
import netsvc

from osv import fields, osv
from tools.translate import _

class ProductImages(osv.osv):
    "Products Image gallery"
    _inherit = "product.images"

    previewed_file_types = ['.png', '.jpg', '.jpeg', '.gif']

    def get_image(self, cr, uid, id):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        image = self.read(cr, uid, id, ['link', 'filename', 'image'])
        res_img = None
        if image['link']:
            if image['filename']:
                file, ext = os.path.splitext(image['filename'])
                if ext.lower() not in self.previewed_file_types:
                    return False
                try :
                    (filename, header) = urllib.urlretrieve(os.path.join(company.local_media_repository, image['filename']))
                    f = open(filename , 'rb')
                    res_img = base64.encodestring(f.read())
                    f.close()
                except:
                    return False #Volunteer silent path if image does not exists on FS in order to be able to access form view
        else:
            res_img = image['image']
        return res_img

ProductImages()
