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

class create_model_wizard(osv.osv_memory):
    _name = 'django.create.model.wizard'

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

    def create_model(self, cr, uid, ids, data, context={}):
        """
        Create Django model from OpenObject Model
        Django Field: http://docs.djangoproject.com/en/dev/ref/models/fields/
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
        model_name = model.split('.')
        if len(model_name) > 0:
            for model in model_name:
                djmodel_name += model.capitalize()
        else:
            djmodel_name += model_name[0].capitalize()

        djmodel = ''
        djmodel += 'from django.db import models\n'
        djmodel += 'from django.utils.translation import ugettext_lazy as _\n'
        djmodel += 'from transmeta import TransMeta\n'
        djmodel += '\n'
        djmodel += 'class %s(models.Model):\n' % djmodel_name
        djmodel += '    """%s OpenERP"""\n'  % djmodel_name
        djmodel += '    __metaclass__ = TransMeta\n'
        djmodel += '\n'

        if len(fields) > 0:
            for field_id in fields:
                field = self.pool.get('ir.model.fields').browse(cr, uid, field_id)
                field_extra_values = ''

                if field.required is False:
                    field_extra_values += ', null=True, blank=True'

                if field.ttype == 'char':
                    djmodel += "    %s = models.CharField(_('%s'), max_length=%s%s)\n" % (field.name, field.field_description, field.size or 128, field_extra_values)
                    if field.name == 'name':
                        title = True

                elif field.ttype == 'boolean':
                    djmodel += "    %s = models.BooleanField(_('%s'), default=False%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'integer':
                    djmodel += "    %s = models.IntegerField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'date':
                    djmodel += "    %s = models.DateField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'datetime':
                    djmodel += "    %s = models.DateTimeField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'time':
                    djmodel += "    %s = models.TimeField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'text':
                    djmodel += "    %s = models.TextField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'float':
                    djmodel += "    %s = models.DecimalField(_('%s'), max_digits=, decimal_places=) #TODO: Digits and decimals\n" % (field.name, field.field_description) #TODO: digits & decimals

                elif field.ttype == 'selection':
                    choices_name = field.name.swapcase()+'_CHOICES'
                    djmodel += "    "+choices_name+" = () #TODO: Selection Options and default value\n" #TODO: Selection Options
                    djmodel += "    %s = models.CharField(_('%s'), choices=%s, default='', max_length=40)\n" % (field.name, field.field_description, choices_name) 

                elif field.ttype == 'binary':
                    djmodel += "    %s = models.FileField(_('%s')%s)\n" % (field.name, field.field_description, field_extra_values)

                elif field.ttype == 'many2one':
                    relation_name = field.relation.split('.')
                    djrelation_name = ''
                    if len(relation_name) > 0:
                        for relation in relation_name:
                            djrelation_name += relation.capitalize()
                    else:
                        djrelation_name += relation_name[0].capitalize()
                    djmodel += "    %s = models.ForeignKey('%s'%s)\n" % (field.name, djrelation_name, field_extra_values)

                #one2many
                    djmodel += "    #%s - _('%s') #one2many field\n" % (field.name, field.field_description)

                #many2many
                elif field.ttype == 'many2many':
                    relation_name = field.relation.split('.')
                    djrelation_name = ''
                    if len(relation_name) > 0:
                        for relation in relation_name:
                            djrelation_name += relation.capitalize()
                    else:
                        djrelation_name += relation_name[0].capitalize()
                    djmodel += "    %s = models.ManyToManyField('%s',db_table = '', related_name='', blank=True) #TODO: Related table. Delete prefix table and ids\n" % (field.name, djrelation_name)

                #others fields TODO: Add list
                else:
                    djmodel += "    #%s = models.%s(%s)\n" % (field.name, field.ttype, field.field_description)

        djmodel += "\n"

        # table name
        djmodel += '    class Meta:\n'
        djmodel += "        db_table = '%s'\n" % table_name
        djmodel += "        #translate = ('', ) #TODO: Translated fields\n"

        djmodel += "\n"

        #title model
        if title:
            djmodel += '    def __unicode__(self):\n'
            djmodel += '        return self.name\n'

        values = {
            'state':'done',
            'file': base64.encodestring(djmodel),
            'filename': 'models.py',
        }
        self.write(cr, uid, ids, values)

        return True

create_model_wizard()
