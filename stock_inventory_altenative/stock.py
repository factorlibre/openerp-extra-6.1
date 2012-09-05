#!/usr/bin/python
#-*- encoding: utf8 -*-

from osv import osv
import time


class stock_inventory(osv.osv):
    _inherit = "stock.inventory"

    def action_done(self, cr, uid, ids, context=None):
        def get_stock_qty(pid, loc_id, uom, to_date=False):
            if to_date:
                return stock_location_obj._product_get(cr, uid, loc_id, [pid], {'uom': uom, 'to_date': to_date})[pid]
            else:
                return stock_location_obj._product_get(cr, uid, loc_id, [pid], {'uom': uom})[pid]
        # END get_stock_qty.

        def chunks(lst, n):
            """ Yield successive n-sized chunks from lst."""
            for i in xrange(0, len(lst), n):
                yield lst[i:i+n]
        # END chunks.

        DEFAULT_UOM_ID = 1

        product_obj = self.pool.get('product.product')
        stock_location_obj = self.pool.get('stock.location')
        uom_obj = self.pool.get('product.uom')

        location_ids = stock_location_obj.search(cr, uid, [('usage', '=', 'internal'), ('chained_location_type', '<>', 'customer')])
        locations = dict([(item.id, item) for item in stock_location_obj.browse(cr, uid, location_ids)])

        uom_ids = uom_obj.search(cr, uid, [])
        uoms = dict([(item.id, item) for item in uom_obj.browse(cr, uid, uom_ids)])

        for inv in self.browse(cr, uid, ids):
            move_ids = []

            location_dict = {}
            for line in inv.inventory_line_id:
                pid = line.product_id.id
                location_dict.setdefault(pid, {})
                qty = uom_obj._compute_qty_obj(cr, uid, uoms[line.product_uom.id], line.product_qty, line.product_id.product_tmpl_id.uom_id)

                if location_dict[pid].get(line.location_id.id):
                    location_dict[pid][line.location_id.id]['qty'] += qty
                else:
                    location_dict[pid][line.location_id.id] = {
                    'qty': qty,
                    'uom': line.product_uom.id,
                    'location_name': line.location_id.name,
                }

            # add products not in the inventory to set their quantity to zero:
            already_processed_product_ids = location_dict.keys()

            # products not in inventory:
            other_product_ids = product_obj.search(cr, uid, [('id', 'not in', already_processed_product_ids)])
            other_product_having_qty_sup_to_zero = {}
            # 10    -> 143
            # 100   -> 93
            # 1000  -> 101
            chunk_len = 100
            for lst_part in chunks(other_product_ids, chunk_len):
                other_product_qty = product_obj._product_available(cr, uid, lst_part, ['qty_available'])
                other_product_having_qty_sup_to_zero.update(dict([(k, v['qty_available']) for k, v in other_product_qty.items() if v['qty_available']]))

            location_dict.update(dict([(other_pid, {}) for other_pid in other_product_having_qty_sup_to_zero.keys()]))

            for pid, location_ids in location_dict.items():
                vals = None
                default_location_id = product_obj.read(cr, uid, pid, ['property_stock_inventory'])['property_stock_inventory'][0]

                for loc_id, vals in location_ids.items():
                    # create move line using difference between product qty for this location
                    # and current qty in stock for this location:

                    change = get_stock_qty(pid, loc_id, vals['uom'], inv.date) - vals['qty']
                    if change:
                        value = {
                            'name': 'INV:%s:%s' % (inv.id, inv.name),
                            'product_id': pid,
                            'product_uom': vals['uom'],
                            'date': inv.date,
                            'date_planned': inv.date,
                            'state': 'assigned'
                        }
                        if change > 0:
                            value.update({
                                'product_qty': change,
                                'location_id': loc_id,
                                'location_dest_id': default_location_id,
                            })
                        else:
                            value.update({
                                'product_qty': -change,
                                'location_id': default_location_id,
                                'location_dest_id': loc_id,
                            })
                        move_ids.append(self.pool.get('stock.move').create(cr, uid, value))

                # set other locations stock quantity to zero:
                other_location_ids = set(locations.keys()).difference(set(location_ids.keys()))
                for loc_id in other_location_ids:
                    # create move line that nullify the current qty in stock for this location:
                    change = get_stock_qty(pid, loc_id, DEFAULT_UOM_ID, inv.date)
                    if change:
                        value = {
                            'name': 'INV:%s:%s' % (inv.id, inv.name),
                            'product_id': pid,
                            'product_uom': DEFAULT_UOM_ID,
                            'date': inv.date,
                            'date_planned': inv.date,
                            'state': 'assigned'
                        }
                        if change > 0:
                            value.update({
                                'product_qty': change,
                                'location_id': loc_id,
                                'location_dest_id': default_location_id,
                            })
                        else:
                            value.update({
                                'product_qty': -change,
                                'location_id': default_location_id,
                                'location_dest_id': loc_id,
                            })
                        move_ids.append(self.pool.get('stock.move').create(cr, uid, value))

            if len(move_ids):
                self.pool.get('stock.move').action_done(cr, uid, move_ids, context=context)
                self.write(cr, uid, [inv.id], {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S'), 'move_ids': [(6, 0, move_ids)]}, context=context)
                self.pool.get('stock.move').write(cr, uid, move_ids, {'date_planned': inv.date, 'date': inv.date}, context=context)

        return True

stock_inventory()


class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    def on_change_product_id(self, cr, uid, ids, location_id, product, uom=False):
        return {'value': {'product_uom': 1, 'product_qty': 1}}

stock_inventory_line()

