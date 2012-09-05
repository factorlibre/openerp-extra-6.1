# -*- encoding: utf-8 -*-

from osv import osv, fields
from addons.decimal_precision import decimal_precision as dp

import time

class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"

    _columns = {
        'discount_1': fields.float('Discount 1',
                                   digits_compute=dp.get_precision('Account'),
                                   help='First discount in %.'),
        'discount_2': fields.float('Discount 2',
                                   digits_compute=dp.get_precision('Account'),
                                   help='Second discount in %.'),
        'discount_3': fields.float('Discount 3',
                                   digits_compute=dp.get_precision('Account'),
                                   help='Third discount in %.'),
        }

    def onchange_3_discount(self, cr, uid, ids, discount_1, discount_2,
                                                discount_3, context=None):
        """Description of the method
        @param self: this object
        @param cr: cursor
        @param uid: user identifier
        @param discount_1...discount_3: values to recompute new values
        @parem context: default context of the record
        @return: return id of the created object
        """
        if context is None:
            context = {}
        res = {}
        name = []
        if discount_1:
            name.append(int(discount_1) == discount_1 and \
                            str(int(discount_1)) + '%' or str(discount_1) + '%')
        else:
            discount_1 = 0.0
        if discount_2:
            name.append(int(discount_2) == discount_2 and \
                            str(int(discount_2)) + '%' or str(discount_2) + '%')
        else:
            discount_2 = 0.0
        if discount_3:
            name.append(int(discount_3) == discount_3 and \
                            str(int(discount_3)) + '%' or str(discount_3) + '%')
        else:
            discount_3 = 0.0

        res['name'] = '+'.join(name)
        res['price_discount'] = -(1 - (1 - discount_1 / 100) * \
                                    (1 - discount_2 / 100) * \
                                    (1 - discount_3 / 100))
        return {
            'value':res
        }

product_pricelist_item()

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"

    def price_description_get(self, cr, uid, pricelist_ids, product_id, qty, context=None):

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        product_obj = self.pool.get('product.product')
        product_category_obj = self.pool.get('product.category')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')

        if pricelist_ids:
            pricelist_version_ids = pricelist_ids
        else:
            # all pricelists:
            pricelist_version_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = list(set(pricelist_version_ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]

        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        if len(pricelist_version_ids) != len(plversion_ids):
            msg = _("At least one pricelist has no active version!\nPlease create or activate one.")
            raise osv.except_osv(_('Warning !'), msg)

        # product.product:
        products = product_obj.browse(cr, uid, [product_id], context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = ''
        tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False

        categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
        categ_ids = _create_parent_category_list(categ_id, [categ_id])
        if categ_ids:
            categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
        else:
            categ_where = '(categ_id IS NULL)'

        cr.execute(
            'SELECT i.*, pl.currency_id '
            'FROM product_pricelist_item AS i, '
                'product_pricelist_version AS v, product_pricelist AS pl '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                'AND (product_id IS NULL OR product_id = %s) '
                'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                'AND price_version_id = %s '
                'AND (min_quantity IS NULL OR min_quantity <= %s) '
                'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
            'ORDER BY sequence',
            (tmpl_id, product_id, plversion_ids[0], qty))
        res1 = cr.dictfetchall()
        for res in res1:
            if res:
                if res['base'] == -1 and res['base_pricelist_id']:
                    based_pricelist = self.price_description_get(cr, uid,
                                                [res['base_pricelist_id']],
                                                product_id, qty, context)
                    if  res['name']:
                        results = '(' + based_pricelist + ')' + res['name']
                    else:
                        results = '(' + based_pricelist + ')'
                else:
                    if  res['name']:
                        results = res['name']
                    else:
                        results = ''
                break

        return results

product_pricelist()
