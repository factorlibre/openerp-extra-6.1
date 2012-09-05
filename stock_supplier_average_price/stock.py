# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
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

from osv import osv
import netsvc

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    # FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty = {}
            prodlot_ids = {}
            product_avail = {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % (move.id), {})
                product_uom = partial_data.get('product_uom') or False
                product_qty = partial_data.get('product_qty') or 0.0
                #Commented in order to process the less number of stock moves from partial picking wizard
                #assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
                move_product_qty[move.id] = product_qty
                product_price = partial_data.get('product_price') or 0.0
                product_currency = partial_data.get('product_currency') or False
                prodlot_id = partial_data.get('prodlot_id') or False
                prodlot_ids[move.id] = prodlot_id
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                product = product_obj.browse(cr, uid, move.product_id.id)
                return_picking = pick.name and '-return' in pick.name or False
                if pick.type == 'in' and move.product_id.cost_method == 'average' and not return_picking:
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                elif pick.type == 'out' and move.product_id.cost_method == 'average' and return_picking:
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id) * -1
                else:
                    continue
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                if product.id in product_avail:
                    product_avail[product.id] += qty
                else:
                    product_avail[product.id] = product.qty_available
                new_price = currency_obj.compute(cr, uid, product_currency,
                        move_currency_id, product_price)
                new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                        product.uom_id.id)
                amount_unit = product.price_get('standard_price', context)[product.id]
                if product.qty_available <= 0:
                    new_std_price = new_price
                elif product_avail[product.id] + qty <= 0:
                    # Returning all products to supplier we not change the std price
                    new_std_price = amount_unit
                else:
                    # Get the standard price
                    new_std_price = ((amount_unit * product_avail[product.id])\
                        + (new_price * qty)) / (product_avail[product.id] + qty)
                if new_std_price <= 0:
                    # Returning products to supplier we can get negative prices.
                    # In this case we not change the std price
                    new_std_price = amount_unit
                # Write the field according to price type field
                product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                # Record the values that were chosen in the wizard, so they can be
                # used for inventory valuation if real-time valuation is enabled.
                move_obj.write(cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})

            for move in too_few:
                product_qty = move_product_qty[move.id]

                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s' % (pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)

                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - product_qty,
                            'product_uos_qty':move.product_qty - product_qty, #TODO: put correct uos_qty
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})

            for move in complete:
                if prodlot_ids.get(move.id):
                    move_obj.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids[move.id]})

            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"

    # FIXME: needs refactoring, this code is partially duplicated in stock_picking.do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % (move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
            product_qty = partial_data.get('product_qty', 0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom', False)
            product_price = partial_data.get('product_price', 0.0)
            product_currency = partial_data.get('product_currency', False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            product = product_obj.browse(cr, uid, move.product_id.id)
            return_picking = move.picking_id.name and '-return' in move.picking_id.name or False
            if move.picking_id.type == 'in' and move.product_id.cost_method == 'average' and not return_picking:
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
            elif move.picking_id.type == 'out' and move.product_id.cost_method == 'average' and return_picking:
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id) * -1
            else:
                continue
            move_currency_id = move.company_id.currency_id.id
            context['currency_id'] = move_currency_id
            new_price = currency_obj.compute(cr, uid, product_currency,
                    move_currency_id, product_price)
            new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                    product.uom_id.id)
            amount_unit = product.price_get('standard_price', context)[product.id]
            if product.qty_available <= 0:
                new_std_price = new_price
            elif product.qty_available + qty <= 0:
                # Returning all products to supplier we not change the std price
                new_std_price = amount_unit
            else:
                # Get the standard price
                new_std_price = ((amount_unit * product.qty_available)\
                    + (new_price * qty)) / (product.qty_available + qty)
            if new_std_price <= 0:
                # Returning products to supplier we can get negative prices.
                # In this case we not change the std price
                new_std_price = amount_unit

            product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

            # Record the values that were chosen in the wizard, so they can be
            # used for inventory valuation if real-time valuation is enabled.
            self.write(cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency,
                        })

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty' : move.product_qty - product_qty,
                        'product_uos_qty':move.product_qty - product_qty,
                    })


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]

stock_move()

