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

import sys, StringIO
import pooler

import wizard


_export_select_form = '''<?xml version="1.0"?>
<form string="Products Export">
<separator string="Select the Web Shop and the rows to export" colspan="4" />
<field name="web_shop"/>
<newline />
<field name="target"/>
<newline />
<label string="" />
<newline />
<label string="To add a Product for exporting, just add a Web Category to it." colspan="4" />
</form>'''

_export_select_fields = {
    'web_shop': {
        'string': 'Web Shop',
        'type': 'many2one',
        'relation': 'esale_joomla.web',
        'required': True,
    },
    'target': {
        'string': 'Which Rows',
        'type': 'selection',
        'selection': [('last', 'new, modified and deleted since last export'), ('all', 'all rows')],
        'default': lambda *a: 'last',
        'required': True,
    },
}

_export_select_form_product = '''<?xml version="1.0"?>
<form string="Products Export">
<separator string="Select the Web Shop and the rows to export" colspan="4" />
<field name="web_shop"/>
</form>'''

_export_select_fields_product = {
    'web_shop': {
        'string': 'Web Shop',
        'type': 'many2one',
        'relation': 'esale_joomla.web',
        'required': True,
    },
}

_export_done_form = '''<?xml version="1.0"?>
<form string="Products Export">
    <separator string="Result" colspan="4" />
    <field name="new"/>
    <newline/>
    <field name="update"/>
    <newline/>
    <field name="delete"/>
    <newline/>
    <field name="error"/>
    <separator string="Error Log" colspan="4" />
    <field name="log" nolabel="1" colspan="4"/>
</form>'''

_export_done_fields = {
    'new': {'string': 'New Products', 'type': 'integer', 'readonly': True},
    'update': {'string': 'Updated Products', 'type': 'integer', 'readonly': True},
    'delete': {'string': 'Deleted Products', 'type': 'integer', 'readonly': True},
    'error': {'string': 'Errors', 'type': 'integer', 'readonly': True},
    'log': {'string': 'Log', 'type': 'text', 'readonly': True},
}


def _export_setup(self, cr, uid, data, context):
    web_shop = 0
    if data['model'] == 'esale_joomla.web':
        web_shop = data['id']
    else:
        ids = pooler.get_pool(cr.dbname).get('esale_joomla.web').search(cr, uid, [('active', '=', '1')])
        if len(ids):
            web_shop = ids[0]
    return {
        'web_shop': web_shop
    }

def _export_from_product(self, cr, uid, data, context):
    stderr = sys.stderr
    sys.stderr = StringIO.StringIO()
    rnew = rupdate = rdelete = rerror = 0
    try:
        if data['model'] != 'product.product':
            print >> sys.stderr, "Function called not allowed from this model %s" % data['model']
        else:
            pool = pooler.get_pool(cr.dbname)
            esale_joomla_product_map_obj = pool.get('esale_joomla.product_map')
            esale_joomla_category_map_obj = pool.get('esale_joomla.category_map')
            web_id = data['form']['web_shop']
            prod_ids = data['ids']
            catmap_ids = pool.get('esale_joomla.category_map').search(cr, uid, [('web_id', '=', web_id), ('esale_joomla_id', '!=', 0), ('category_id', '!=', False)]) #get categories for selected shop
            if not catmap_ids:
                print >> sys.stderr, "No categories for this web shop"
            else:
                webcategories = {}
                for x in esale_joomla_category_map_obj.read(cr, uid, catmap_ids, ['category_id', 'esale_joomla_id'], context=context):
                    webcategories[x['category_id'][0]] = x['esale_joomla_id']
                (rnew, rupdate, rdelete, rerror) = esale_joomla_product_map_obj.webexport_product(cr, uid, web_id, prod_ids, webcategories, context)
    finally:
        log = sys.stderr.getvalue()
        sys.stderr.close()
        sys.stderr = stderr
    return {'new': rnew, 'update': rupdate, 'delete': rdelete, 'error': rerror, 'log': log}

def _export_from_shop(self, cr, uid, data, context):
    stderr = sys.stderr
    sys.stderr = StringIO.StringIO()
    rnew = rupdate = rdelete = rerror = 0

    try:
        pool = pooler.get_pool(cr.dbname)
        esale_joomla_product_map_obj = pool.get('esale_joomla.product_map')
        esale_joomla_category_map_obj = pool.get('esale_joomla.category_map')

        web_id = data['form']['web_shop']
        catmap_ids = pool.get('esale_joomla.category_map').search(cr, uid, [('web_id', '=', web_id), ('esale_joomla_id', '!=', 0), ('category_id', '!=', False)]) #get categories for selected shop
        if not catmap_ids:
           print >>sys.stderr, "No categories for this web shop"
        else:
            webcategories = {}
            for x in esale_joomla_category_map_obj.read(cr, uid, catmap_ids, ['category_id', 'esale_joomla_id'], context=context):
                webcategories[x['category_id'][0]] = x['esale_joomla_id']
            if data['form']['target'] != 'last':
                sql = "select distinct r.product_id from esale_category_product_rel r"
                sql += "  where r.category_id in (%s);" % ','.join(map(str, webcategories.keys()))
            else:
                sql = "select distinct r.product_id from esale_category_product_rel r"
                sql += "  inner join product_product p on p.id=r.product_id"
                sql += "  left outer join esale_joomla_product_map m on p.id=m.product_id"
                sql += "  where r.category_id in (%s)" % ','.join(map(str, webcategories.keys()))
                sql += "    and m.export_date is NULL or m.state='error' or (p.create_date > m.export_date or p.write_date > m.export_date);"
            cr.execute(sql)
            prod_ids = map(lambda x: x[0], cr.fetchall())
            (rnew, rupdate, rdelete, rerror) = esale_joomla_product_map_obj.webexport_product(cr, uid, web_id, prod_ids, webcategories, context)

    finally:
        log = sys.stderr.getvalue()
        sys.stderr.close()
        sys.stderr = stderr
    return {
        'new': rnew,
        'update': rupdate,
        'delete': rdelete,
        'error': rerror,
        'log': log,
    }


class wiz_export(wizard.interface):
    states = {
        'init': {
            'actions': [_export_setup],
            'result': {
                'type': 'form',
                'arch': _export_select_form,
                'fields': _export_select_fields,
                'state': [('export', 'Export', 'gtk-execute'), ('end', 'Cancel', 'gtk-cancel')],
            },
        },
        'export': {
            'actions': [_export_from_shop],
            'result': {
                'type': 'form',
                'arch': _export_done_form,
                'fields': _export_done_fields,
                'state': [('end', 'End')],
            },
        },
    }

wiz_export('esale_joomla.web.wizard.export.products')

class wiz_export_from_product(wizard.interface):
    states = {
        'init': {
            'actions': [_export_setup],
            'result': {
                'type': 'form',
                'arch': _export_select_form_product,
                'fields': _export_select_fields_product,
                'state': [('export', 'Export', 'gtk-execute'), ('end', 'Cancel', 'gtk-cancel')],
            },
        },
        'export': {
            'actions': [_export_from_product],
            'result': {
                'type': 'form',
                'arch': _export_done_form,
                'fields': _export_done_fields,
                'state': [('end', 'End')],
            },
        },
    }

wiz_export_from_product('esale_joomla.product_map.wizard.export')

# vim:et:
