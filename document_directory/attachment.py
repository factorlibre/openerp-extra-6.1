# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
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

from osv import osv, fields
from tools.translate import _

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"

    def __get_def_model_directory(self, cr, uid, context=None):
        """Get default directory from object.
        If don't exists directory object, use 'document' directory.
        """

        default_directory = False
        default_model = context.get('default_res_model',False)

        if default_model:
            models = self.pool.get('ir.model').search(cr, uid, [('model','=',default_model)])
            if len(models) > 0:
                directoris = self.pool.get('document.directory').search(cr, uid, [('ressource_parent_type_id','=',models[0])])
                if len(directoris) > 0:
                    return directoris[0]

        if not default_directory:
            #default directory: document
            dirobj = self.pool.get('document.directory')
            return dirobj._get_root_directory(cr, uid, context)

    _defaults = {
        'parent_id': __get_def_model_directory,
    }

ir_attachment()
