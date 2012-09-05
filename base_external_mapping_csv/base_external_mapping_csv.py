# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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

class base_external_mapping(osv.osv):
    _inherit = 'base.external.mapping'

    _columns = {
        'csv': fields.boolean('CSV', help="CSV Mapping"),
        'csv_path': fields.char('Path', size=300, help="The path to the file name. The last slash is not necessary"),
        'csv_file':fields.char('CSV File', size=64, help='CSV Filename'),
        'csv_header': fields.boolean('Header', help="Header (fields name) on files"),
        'csv_file_separator': fields.selection([
            (',','Comma'),
            (';','Semicolon'),
            ('tab','Tabulator')
        ], 'CSV Separator', help="Product File CSV Separator"),
        'csv_quote': fields.char('Quote', size=1, help="Character to use as quote"),
    }

base_external_mapping()
