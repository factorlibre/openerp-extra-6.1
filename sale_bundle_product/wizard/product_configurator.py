# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_bundle_product for OpenERP                                          #
# Copyright (c) 2011 CamptoCamp. All rights reserved. @author Joel Grand-Guillaume #
# Copyright (c) 2011 Akretion. All rights reserved. @author Sébastien BEAU      #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


from osv import fields, osv
from tools.translate import _

class product_configurator(osv.osv_memory):
    _name = "product.item.set.configurator"
    _description = "Product Configurator"
    _columns = {
     }
     
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values

        @return : default values of fields.
        """
        sale_item_line_obj = self.pool.get('sale.order.line.item.set')
        product_item_obj = self.pool.get('product.item.set')
        res = super(product_configurator, self).default_get(cr, uid, fields, context=context)
        so_line_item_set_ids = self.pool.get('sale.order.line').read(cr, uid, context['order_line_id'], ['so_line_item_set_ids'], context=context)['so_line_item_set_ids']
        item_set_ids = product_item_obj.search(cr, uid, [['name', 'in', fields]], context=context)
        for item_set in product_item_obj.browse(cr, uid, item_set_ids, context):
            if item_set.multi_select:
                res[item_set.name]=[]
            else:
                res[item_set.name]=False
            for item_line in item_set.item_set_line_ids:
                sale_line_ids = sale_item_line_obj.search(cr, uid, [
                        ['id', 'in', so_line_item_set_ids],
                        ['product_id', '=', item_line.product_id.id],
                        ['uom_id', '=', item_line.uom_id.id],
                        ['qty_uom', '=', item_line.qty_uom]
                    ], context=context)
                #if a sale item line is found it's mean that the product item was choosen with the configurator
                if sale_line_ids:
                    if item_set.multi_select:
                        res[item_set.name].append(item_line.id)
                    else:
                        res[item_set.name]=item_line.id
                        break
        return res
        
    def set_configuration(self, cr, uid, *args):
        '''empty function'''
        return {}
    
    def create(self, cr, uid, vals, context=None):
        item_line_ids=[]
        for key in vals:
            if type(vals[key]) == list:
                item_line_ids += vals[key][0][2]
            else:
                item_line_ids += [vals[key]]
        sale_item_ids = self.pool.get('product.item.set.line').get_sale_items_lines(cr, uid, item_line_ids, context)
        self.pool.get('sale.order.line').write(cr, uid, context['order_line_id'], {'so_line_item_set_ids': [(6, 0, sale_item_ids)]}, context=context)
        return 1
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        order_line = self.pool.get('sale.order.line').browse(cr, uid, context['order_line_id'], context)
        
        fields_list = {}
        arch = """<form string="Choose your Configuration">"""
        for item_set in order_line.product_id.item_set_ids:
            field_name = item_set.name.replace(' ', '_')
            arch += """<separator colspan="4" string="%s"/>
                       <field name="%s" nolabel="1" colspan="4"/> """ % (item_set.name, field_name)
            if item_set.multi_select:
                fields_list.update({field_name:{
                                'domain': [['item_set_id', '=', item_set.id]],
                                'string' : item_set.name,
                                'type' : 'many2many',
                                'relation': 'product.item.set.line',
                                'related_columns': ['test_id', 'item_id'],
                                'third_table': '%s_item_rel' % field_name,
                                'selectable': True,
                                }
                            })
            else:
                fields_list.update({field_name:{
                                'domain': [['item_set_id', '=', item_set.id]],
                                'string': 'Attribute Set',
                                'type': 'many2one',
                                'relation': 'product.item.set.line',
                                'selectable': True,
                                }
                            })
        
        arch += """
                <group col="2" colspan="2">
                <button icon='gtk-cancel' special="cancel"
                    string="_Cancel" />
                <button name="set_configuration" string="Validate"
                    colspan="1" type="object" icon="gtk-go-forward" />
                </group>
        </form>"""
        
        return {
            'name': 'Choose Your Configuration',
            'type': 'form',
            'fields': fields_list,
            'model': 'stock.partial.picking',
            'arch': arch,
            'field_parent': False}


product_configurator()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
