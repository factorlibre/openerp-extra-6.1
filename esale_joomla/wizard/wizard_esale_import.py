#!/usr/bin/python
# -*- coding: utf-8
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler
import sys, StringIO


_import_select_form = '''<?xml version="1.0"?>
<form string="Sale Orders Import">
<separator string="Select the Web Shop to import" colspan="4" />
<field name="web_shop"/>
<newline />
</form>'''

_import_select_fields = {
    'web_shop': {
        'string': 'Web Shop',
        'type': 'many2one',
        'relation': 'esale_joomla.web',
        'required': True,
    },
##     'target': {
##         'string': 'Which Rows',
##         'type': 'selection',
##         'selection': [('last', 'new, modified and deleted since last import'), ('all', 'all rows')],
##         'default': lambda *a: 'last',
##         'required': True,
##     },
}

_import_done_form = '''<?xml version="1.0"?>
<form string="Web Sale Orders Import">
    <separator string="Result" colspan="4" />
    <field name="new"/>
    <newline/>
    <field name="update"/>
    <newline/>
    <field name="error"/>
    <separator string="Error Log" colspan="4" />
    <field name="log" nolabel="1" colspan="4"/>
</form>'''

_import_done_fields = {
    'new': {
        'string': 'New Web Sale Orders',
        'type': 'integer',
        'readonly': True,
    },
    'update': {
        'string': 'Updated Web Sale Orders',
        'type': 'integer',
        'readonly': True,
    },
    'error': {
        'string': 'Errors',
        'type': 'integer',
        'readonly': True,
    },
    'log': {
        'string': 'Log',
        'type': 'text',
        'readonly': True,
    },
}


def _import_setup(self, cr, uid, data, context):
    web_shop = 0
    if data['model'] == 'esale_joomla.web':
        web_shop = data['id']
    elif data['model'] == 'esale_joomla.order':
        cats = pooler.get_pool(cr.dbname).get('esale_joomla.order').browse(cr, uid, data['ids'])
        if len(cats):
            web_shop = cats[0].web_id.id
    else:
        ids = pooler.get_pool(cr.dbname).get('esale_joomla.web').search(cr, uid, [('active', '=', True)])
        if len(ids):
            web_shop = ids[0]
    return {'web_shop': web_shop}


def _import_from_shop(self, cr, uid, data, context):
    stderr = sys.stderr
    sys.stderr = StringIO.StringIO()
    rnew = rupdate = rerror = 0
    try:
        self.pool = pooler.get_pool(cr.dbname)
        web_id = data['form']['web_shop']
        #target = data['form']['target']
        #(rnew, rupdate, rerror) = self.pool.get('esale_joomla.order').webimport(cr, uid, [web_id], target)
        (rnew, rupdate, rerror) = self.pool.get('esale_joomla.order').webimport(cr, uid, [web_id])
    finally:
        log = sys.stderr.getvalue()
        sys.stderr.close()
        sys.stderr = stderr
    return {'new': rnew, 'update': rupdate, 'error': rerror, 'log': log}


class wiz_esale_joomla_import_sale_orders(wizard.interface):
    states = {
        'init': {
            'actions': [_import_setup],
            'result': {
                'type': 'form',
                'arch': _import_select_form,
                'fields': _import_select_fields,
                'state': [('import', 'Import', 'gtk-execute'), ('end', 'Cancel', 'gtk-cancel')],
            },
        },
        'import': {
            'actions': [_import_from_shop],
            'result': {
                'type': 'form',
                'arch': _import_done_form,
                'fields': _import_done_fields,
                'state': [('end', 'End')],
            },
        },
    }

wiz_esale_joomla_import_sale_orders('esale_joomla.saleorders')

