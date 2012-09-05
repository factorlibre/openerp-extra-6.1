# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
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
############################################################################################

from osv import fields,osv
from tools.translate import _

import base64
import time
import re

class sql_update_wizard(osv.osv_memory):
    _name = 'django.sql.update.wizard'

    _columns = {
        'model': fields.many2one('ir.model','Model', required=True),
        'file':fields.binary('File'),
        'filename': fields.char('File Name', size=32),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
    }

    def sql_update(self, cr, uid, ids, data, context={}):
        """
        Create SQL Update for Django model because Django not reload SQL from Django Model
        """

        form = self.browse(cr, uid, ids[0])
        model = form.model

        #fields
        fields = self.pool.get('ir.model.fields').search(cr, uid,[('model_id', '=', model.id)])

        title = False

        # Model and Table Django Name
        djmodel_name = ''
        model = model.model
        table_name = re.sub('\.', '_', model)

        djmodel = ''

        if len(fields) > 0:
            for field_id in fields:
                field = self.pool.get('ir.model.fields').browse(cr, uid, field_id)
#                field_extra_values = ''

#                if field.required is False:
#                    field_extra_values += 'NOT NULL'

                if field.ttype == 'char':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s varchar(%s); --TODO: Size\n" % (table_name, field.name, field.size or 128)

                elif field.ttype == 'boolean':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s boolean;\n" % (table_name, field.name)

                elif field.ttype == 'integer':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s integer;\n" % (table_name, field.name)

                elif field.ttype == 'date':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s date;\n" % (table_name, field.name)

                elif field.ttype == 'datetime':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s timestamp without time zone;\n" % (table_name, field.name)

                elif field.ttype == 'time':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s time without time zone;\n" % (table_name, field.name)

                elif field.ttype == 'text':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s text;\n" % (table_name, field.name)

                elif field.ttype == 'float':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s numeric(16,2);\n" % (table_name, field.name) #TODO: digits & decimals

                elif field.ttype == 'selection':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s varchar(%s); --TODO: Size\n" % (table_name, field.name, field.size or 128) 

                elif field.ttype == 'binary':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s bytea;\n" % (table_name, field.name)

                elif field.ttype == 'many2one':
                    djmodel += "ALTER TABLE %s ADD COLUMN %s integer;\n" % (table_name, field.name)

                #one2many
#                    djmodel += "#%s #one2many field\n" % (field.name, field.field_description)

                #many2many
#                elif field.ttype == 'many2many':
#                    djmodel += "ALTER TABLE %s ADD COLUMN %s ;\n" % (field.name, djrelation_name)

                #others fields TODO: Add list
                else:
                    djmodel += "--ALTER TABLE %s ADD COLUMN %s;\n" % (table_name, field.name)

        djmodel += "\n"

        values = {
            'state':'done',
            'file': base64.encodestring(djmodel),
            'filename': 'models.sql',
        }
        self.write(cr, uid, ids, values)

        return True

sql_update_wizard()
