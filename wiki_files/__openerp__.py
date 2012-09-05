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

{
    'name': 'Wiki Files',
    "version": "0.1",
    'category': 'Generic Modules/Others',
    'description': """
Add public files in Wiki Pages (http)
Configure FTP server and publish public files in your Wiki Pages
When editing a wiki page will have a wizard for publishing files on public FTP server and it is available in the files section of the wiki page.
To publish a file, select a file on your hard disk. We propose a file name. This name if contain non-alphanumeric characters (az09) and spaces, it will be removed later.
If an image file, it will be offered image tag to copy and paste
If other type of document, it will be offered link tag to copy and paste
    """,
    "author": "Zikzakmedia SL",
    "website": "http://www.zikzakmedia.com",
    "license" : "AGPL-3",
    'depends': [
        'wiki',
    ],
    'init_xml': [],
    'update_xml': [
        'wiki_files_view.xml',
        'wizard/wiki_files_wizard_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
