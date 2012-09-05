# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
#                       Raimon Esteve <resteve@zikzakmedia.com>
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

from osv import osv, fields
from tools.translate import _

import netsvc
import re
import csv


class csv_file_field(osv.osv):
    _name = 'csv.file.field'

csv_file_field()


class csv_file(osv.osv):

    _name = 'csv.file'
    _columns = {
        'name': fields.char('Code', size=64, required=True, help="Code Name of this file. Use lowcase and az09 characters."),
		'path': fields.char('Path', size=300, required=True, help="The path to the file name. The last slash is not necessary"),
        'state' : fields.selection([('draft', 'Draft'),('done', 'Done')],'State',required=True,readonly=True),
        'file':fields.char('CSV File', required=True, size=64, help='CSV Filename'),
        'file_csv_separator': fields.selection([
            (',','Comma'),
            (';','Semicolon'),
            ('tab','Tabulator')
        ], 'CSV Separator', required=True, help="Product File CSV Separator"),
		'header': fields.boolean('Header', help="Header (fields name) on files"),
		'quote': fields.char('Quote', size=1, required=True, help="Character to use as quote"),
		'field_ids': fields.one2many('csv.file.field','file_id','Fields'),
        'model_id': fields.many2one('ir.model', 'OpenERP Model', required=True, select=True, ondelete='cascade'),
        'model':fields.related('model_id', 'model', type='char', string='Model Name', readonly=True),
	}

    _defaults = {
        'quote': lambda *a: '',
        'file_csv_separator':lambda *a: ",",
        'state' : lambda *a: 'draft',
    }

    def create(self, cr, uid, vals, context=None):
        vals['name']  = re.sub(r'\W+', '',vals['name']).lower() #replace name to az09 characters and lowercase
        csv_file_ids = self.pool.get('csv.file').search(cr, uid, [('name','ilike',vals['name'])])
        if len(csv_file_ids) > 0:
            raise osv.except_osv(_('Error!'), _("Another External Mapping have the same code!"))
        vals['state'] = 'done'
        return super(csv_file, self).create(cr, uid, vals, context)

    """
    Lines CSV
    """
    def lines_csv(self, cr, uid, id, context=None):

        num_lines = False

        csv_file = self.browse(cr, uid, id)
        if csv_file:
            csvpath = csv_file.path
            if not csvpath[-1] == '/':
                csvpath += '/'

            csvfile = open(csvpath+csv_file.file, "r")

            num_lines = sum(1 for line in open(csvpath+csv_file.file))

            if csv_file.header:
                num_lines = num_lines-1

        return num_lines

    """
    Import CSV list from line file
    If you have a big CSV file, we recomended use mincalls in this function and use number line
    """
    def import_line_csv(self, cr, uid, ids, line, context=None):
        self.logger = netsvc.Logger()
        csv_file_field_obj = self.pool.get('csv.file.field')

        for csv_file in self.browse(cr, uid, ids):
            csvpath = csv_file.path
            if not csvpath[-1] == '/':
                csvpath += '/'

            csvfile = open(csvpath+csv_file.file, "r")

            separator = csv_file.file_csv_separator
            if separator == "tab":
                separator = '\t'

            csv_values = []

            #if you have a big CSV file, we recomended use mincalls in this function and use number line
            if line:
                csvfile_lines = csvfile.readlines()

                try:
                    csvfile_values = csvfile_lines[line].split(separator)
                except:
                    csvfile_values = []

                values = []

                for cell, value in enumerate(csvfile_values):
                    field_ids = csv_file_field_obj.search(cr, uid, [('file_id','=',csv_file.id), ('sequence','=',cell)])
                    if len(field_ids):
                        csv_file_value = csv_file_field_obj.browse(cr, uid, field_ids[0])

                        if csv_file_value.import_expression:
                            localspace = {"self":self, "cr":cr, "uid":uid, "ids":ids, "re":re, "context":context, "incsv":value, "row":row}
                            code = csv_file_value.import_expression.replace('\r\n', '\n')
                            exec code in localspace
                            if 'value' in localspace:
                                value = localspace['value']
                            else:
                                value = ''

                        values.append({'field':csv_file_value.field_id.name, 'value':value})

                self.logger.notifyChannel(_("CSV File"), netsvc.LOG_INFO, _("Add dicc row line %s") % line)
                csv_values.append(values)
            else:
                self.logger.notifyChannel(_("CSV File"), netsvc.LOG_ERROR, _("Not line specified"))

            csvfile.close()

        return csv_values

    """
    Import CSV
    return all rows in list
    """
    def import_csv(self, cr, uid, ids, context=None):
        self.logger = netsvc.Logger()
        csv_file_field_obj = self.pool.get('csv.file.field')

        csv_values = []

        for csv_file in self.browse(cr, uid, ids):
            csvpath = csv_file.path
            if not csvpath[-1] == '/':
                csvpath += '/'

            csvfile = open(csvpath+csv_file.file, "r")

            separator = csv_file.file_csv_separator
            if separator == "tab":
                separator = '\t'

            rows = csv.reader(csvfile, delimiter="%s" % str(separator))

            for row in rows:
                values = []
                if csv_file.header: # Header file. Skip
                    if rows.line_num == 1:
                        continue
                for cell, value in enumerate(row):
                    field_ids = csv_file_field_obj.search(cr, uid, [('file_id','=',csv_file.id), ('sequence','=',cell)])
                    if len(field_ids):
                        csv_file_value = csv_file_field_obj.browse(cr, uid, field_ids[0])

                        if csv_file_value.import_expression:
                            localspace = {"self":self, "cr":cr, "uid":uid, "ids":ids, "re":re, "context":context, "incsv":value, "row":row}
                            code = csv_file_value.import_expression.replace('\r\n', '\n')
                            exec code in localspace
                            if 'value' in localspace:
                                value = localspace['value']
                            else:
                                value = ''

                        values.append({csv_file_value.field_id.name:value})

                self.logger.notifyChannel(_("CSV File"), netsvc.LOG_INFO, _("Add dicc row line %s") % rows.line_num)
                csv_values.append(values)

            csvfile.close()

        return csv_values

    """
    Export CSV
    """
    def export_csv(self, cr, uid, ids, context=None):
        #TODO. Design this function. You can inspire code in nan_file_format module

        return False

csv_file()


class csv_file_field(osv.osv):
    _name = 'csv.file.field'

    _columns = {
		'name': fields.char('Name',size=64, required=True, help="The name of the field. It's used if you have selected the Header checkbox"),
		'sequence': fields.integer('Sequence', help="Is the order that you want for the columns field in the file"),
        'field_id': fields.many2one('ir.model.fields', 'OpenERP Field', select=True, ondelete='cascade', required=True, domain="[('model_id', '=', parent.model_id),('ttype','!=','binary')]"),
		'file_id': fields.many2one('csv.file','External Mapping'),
#		'header': fields.related('file_id','header', type='boolean', string='Header'), #TODO: name or sequence visible if header true or false
		'import_expression': fields.text('Import Expression', help="Where we put the python code. The fields are called like '$name_of_field' (without the simple quotes)"),
		'export_expression': fields.text('Export Expression', help="Where we put the python code. The fields are called like '$name_of_field' (without the simple quotes)"),
        'type': fields.selection([('str', 'String'), ('bool', 'Boolean'), ('int', 'Integer'), ('float', 'Float')], 'Type'),
    }

    _order = 'sequence'

    _defaults = {
        'type': lambda *a: 'str',
    }

csv_file_field()
