# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import time

class product_state(osv.osv):
    _name = "product.state"
    _description = "States of Books"
    _columns={
        'name': fields.char('State', size=64, select=1, required=True),
        'code': fields.char('Code', size=64, required=True),
        'active': fields.boolean('Active', select=2),
        }
product_state()

class many2manysym(fields.many2many):

    def get(self, cr, obj, ids, name, user=None, offset=0, context={}, values={}):
        res = {}
        if not ids:
            return res
        ids_s = ','.join(map(str, ids))
        for id in ids:
            res[id] = []
        limit_str = self._limit is not None and ' limit %d' % self._limit or ''

        for (self._id2, self._id1) in [(self._id2, self._id1), (self._id1, self._id2)]:
            cr.execute('select '+self._id2+','+self._id1+' from '+self._rel+' where '+self._id1+' in ('+ids_s+')'+limit_str+' offset %s', (offset,))
            for r in cr.fetchall():
                res[r[1]].append(r[0])
        return res

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'name': fields.char('Name', size=256, required=True, select=True),
        }

product_template()

def _state_get(self, cr, uid,context):
    cr.execute('select name, name from product_state order by name')
    return cr.fetchall()

class product_lang(osv.osv):
    """Book language"""
    _name = "product.lang"

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, translate=True),
        }
product_lang()

class product_product(osv.osv):
    """Book variant of product"""
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []

        def _name_get(d):
            #name = self._product_partner_ref(cr, user, [d['id']], '', '', context)[d['id']]
            #code = self._product_code(cr, user, [d['id']], '', '', context)[d['id']]
            name = d.get('name', '')
            ean = d.get('ean13', False)
            price = d.get('list_price', 0.0)
            if ean or price:
                name = '[%s] [%s] %s' % (ean or '', price, name)
            return (d['id'], name)

        return map(_name_get, self.read(cr, user, ids, ['name', 'ean13', 'list_price'], context))

    def name_search(self, cr, user, name, args=[], operator='ilike', context={}, limit=80):
        ids = self.search(cr, user, [('default_code', '=', name)]+ args, limit=limit)
        if not len(ids):
            ids = self.search(cr, user, [('ean13', '=', name)]+ args, limit=limit)
        if not len(ids):
            ids = self.search(cr, user, [('default_code', operator, name)]+ args, limit=limit)
            ids += self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, user, ids, context)

    def _tax_incl(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for product in self.browse(cr, uid, ids):
            val = 0.0
            for c in self.pool.get('account.tax').compute(cr, uid, product.taxes_id, product.list_price, 1, False):
                val += round(c['amount'], 2)
            res[product.id] = round(val + product.list_price, 2)

        return res


    def create(self, cr, uid, vals, context= None):
        def _uniq(seq):
            keys = {}
            for e in seq:
                keys[e] = 1
            return keys.keys()

        # add link from editor to supplier:
        if 'editor' in vals:
            editor_id = vals['editor']
            supplier_model = self.pool.get('library.editor.supplier')
            supplier_ids = [idn for idn in supplier_model.search(cr, uid, [('name', '=', editor_id)]) if idn > 0]
            suppliers = supplier_model.browse(cr, uid, supplier_ids, context)
            for obj in suppliers:
                supplier = [
                    0, 0, {'pricelist_ids': [], 'name': obj.supplier_id.id, 'sequence': obj.sequence, 'qty': 0,
                    'delay': 1, 'product_code': False, 'product_name': False}
                ]
                if 'seller_ids' not in vals:
                    vals['seller_ids'] = [supplier]
                else:
                    vals['seller_ids'].append(supplier)

        return super(product_product, self).create(cr, uid, vals, context=context)

    _columns = {
        'isbn': fields.char('Isbn code', size=64, unique=True),
        'catalog_num': fields.char('Catalog number', size=64),
        #'number': fields.char('Number', size=64, readonly=True), # ancien numero interne
        'author_om_ids': fields.one2many('author.book.rel', 'product_id', 'Authors'),
        'lang': fields.many2many('product.lang', 'lang_book_rel', 'product_id', 'lang_id', 'Language'),
        'editor': fields.many2one('res.partner', 'Editor', change_default=True),
        'catalog_num': fields.char('Catalog number', size=64),
        'date_parution': fields.date('Release date'),
        'creation_date': fields.datetime('Creation date', readonly=True),
        'date_retour': fields.date('Return date'),
        'tome': fields.char('Tome', size=8),
        'nbpage': fields.integer('Number of pages', size=8),
        'rack': fields.many2one('library.rack', 'Rack', size=16),
        #'state': fields.selection([('draft', 'Not yet published'), ('sellable', 'Available'), ('end', 'Sold Out'), ('obsolete', 'Printing w/o Date')], 'State'),
       # 'state': fields.selection(_state_get, 'State', size=128),
        'availability_id': fields.many2one('product.state', 'State'),
        'link_ids': many2manysym('product.product', 'book_book_rel', 'product_id1', 'product_id2', 'Related Books'),
        'back': fields.selection([('hard', 'Hardback'), ('paper', 'Paperback')], 'Reliure'),
        'collection': fields.many2one('library.collection', 'Collection'),
        'pocket': fields.char('Pocket', size=32),
        'num_pocket': fields.char('Collection Num.', size=32),
        'num_edition': fields.integer('Num. edition'),
        'format': fields.char('Format', size=128),
        'price_cat': fields.many2one('library.price.category', "Price category"),
#       'categ_id': fields.many2one('product.category','Category', required=True, change_default=False),
    }

    _defaults = {
        'creation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'back': lambda *a: 'paper',
        'procure_method': lambda *a: 'make_to_order',
        'date_retour': lambda *a: str(int(time.strftime("%Y"))+1) + time.strftime("-%m-%d"),
    }


product_product()

class author_book_rel(osv.osv):
    _name = "author.book.rel"
    _rec_name = "author_id"
    _columns = {
        'author_id': fields.many2one('library.author', 'Author', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Book', ondelete='cascade')
        }

author_book_rel()

class product_product_in(osv.osv):
    _inherit = "product.product"
    _columns = {
        'author_ids': fields.many2many('library.author', 'author_book_rel', 'product_id', 'author_id', 'Authors'),
        }

    def copy(self, cr, uid, id, default=None, context={}):
        if default is None:
            default = {}
        default.update({'author_ids': []})
        return super(product_product_in, self).copy(cr, uid, id, default, context)
    _constraints = [

    ]

product_product_in()

class library_author(osv.osv):
    _inherit = 'library.author'
    _columns = {
        'book_ids': fields.many2many('product.product', 'author_book_rel', 'author_id', 'product_id', 'Books', select=1),
        }

library_author()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: