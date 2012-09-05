# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import sys, StringIO
import pooler

import wizard


_export_select_form = '''<?xml version="1.0"?>
<form string="Products Export">
<separator string="Select the Web Shop and the rows to export" colspan="4" />
<field name="web_shop"/>
<newline />
<field name="target"/>
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

_export_done_form = '''<?xml version="1.0"?>
<form string="Products Export">
    <separator string="Result" colspan="4" />
    <field name="update"/>
    <newline/>
    <field name="error"/>
    <separator string="Error Log" colspan="4" />
    <field name="log" nolabel="1" colspan="4"/>
</form>'''

_export_done_fields = {
    'update': {'string': 'Updated Products', 'type': 'integer', 'readonly': True},
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


def _export_to_shop(self, cr, uid, data, context):
    stderr = sys.stderr
    sys.stderr = StringIO.StringIO()
    rnew = rupdate = rdelete = rerror = 0

    try:
        pool = pooler.get_pool(cr.dbname)
        esale_joomla_product_map_obj = pool.get('esale_joomla.product_map')
        esale_joomla_category_map_obj = pool.get('esale_joomla.category_map')

        web_id = data['form']['web_shop']
        catmap_ids = pool.get('esale_joomla.category_map').search(cr, uid, [('web_id', '=', web_id), ('esale_joomla_id', '!=', 0), ('category_id', '!=', False)])
        if not catmap_ids:
            print >> sys.stderr, 'No categories for this web shop'
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
            (rupdate, rerror) = esale_joomla_product_map_obj.webexport_stock(cr, uid, web_id, prod_ids, webcategories, context)

    finally:
        log = sys.stderr.getvalue()
        sys.stderr.close()
        sys.stderr = stderr
    return {
        'update': rupdate,
        'error': rerror,
        'log': log,
    }


class wiz_esale_joomla_stocks(wizard.interface):
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
            'actions': [_export_to_shop],
            'result': {
                'type': 'form',
                'arch': _export_done_form,
                'fields': _export_done_fields,
                'state': [('end', 'End')],
            },
        },
    }

wiz_esale_joomla_stocks('esale_joomla.stocks')

## _export_form = '''<?xml version="1.0"?>
## <form string="Initial import" />
## '''
## 
## _export_fields = {}
## 
## _export_done_form = '''<?xml version="1.0"?>
## <form string="Initial import">
## <separator string="Stock succesfully updated" colspan="4" />
## </form>'''
## 
## _export_done_fields = {}
## 
## 
## def _do_export(self, cr, uid, data, context):
##     pool = pooler.get_pool(cr.dbname)
##     esale_joomla_web_obj = pool.get('esale_joomla.web')
##     product_obj = pool.get('product.product')
## 
##     web_ids = esale_joomla_web_obj.search(cr, uid, [('active', '=', 'True')])
##     for website in esale_joomla_web_obj.browse(cr, uid, web_ids):
##         server = xmlrpclib.ServerProxy("%s/tinyerp-synchro.php" % website.url)
## 
##         for osc_product in website.product_ids:
##             if osc_product.esale_joomla_id:
##                 webproduct = {
##                     'esale_joomla_id': osc_product.esale_joomla_id,
##                     'quantity': product_obj._product_virtual_available(cr, uid, [osc_product.product_id.id], '', False, {'shop': website.shop_id.id})[osc_product.product_id.id],
##                 }
##             osc_id = server.set_product_stock(webproduct)
## 
##     return {}

