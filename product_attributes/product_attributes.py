# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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

from osv import osv, fields
import tools
from tools.translate import _
import unicodedata
import re
            
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

class product_attributes(osv.osv):
    _name = 'product.attributes'
    _description = 'Product attributes for product OpenERP module'


    def _get_fields_type(self, cr, uid, context=None):
        cr.execute('select distinct ttype,ttype from ir_model_fields')
        return cr.fetchall()


    def _get_fields_type(self, cr, uid, context=None):
        cr.execute('select distinct ttype,ttype from ir_model_fields')
        field_types = cr.fetchall()
        field_types_copy = field_types

        for types in field_types_copy:
            if not hasattr(fields,types[0]):
                field_types.remove(types)

        return field_types


    def create(self, cr, uid, vals, context=None):
        model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')])[0]

        if 'selection' in vals:
            selection = vals['selection']
        else:
            selection = ''

        if 'relation' in vals:
            relation = vals['relation']
        else:
            relation = ''

        if 'relation_field' in vals:
            relation_field = vals['relation_field']
        else:
            relation_field = ''

        field_vals = {
            'field_description': vals['field_description'],
            'model_id': model_id,
            'model': 'product.product',
            'name': slugify(tools.ustr(vals['name'])),
            'ttype': vals['ttype'],
            'translate': vals['translate'],
            'required': vals['required'],
            'selection': selection,
            'relation': relation,
            'relation_field': relation_field,
            'state': 'manual',
        }
        vals['field_id'] = self.pool.get('ir.model.fields').create(cr, uid, field_vals)
        id = super(product_attributes, self).create(cr, uid, vals, context)
        return id


    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Alert !'), _('You can\'t delete this attribute'))


    def write(self, cr, uid, ids, vals, context=None):
        values = {}
        if 'sequence' in vals:
            values['sequence'] = vals['sequence']
        if 'required' in vals:
            values['required'] = vals['required']
        if 'translate' in vals:
            values['translate'] = vals['translate']

        id = super(product_attributes, self).write(cr, uid, ids, values, context)
        return id

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'field_description': fields.char('Field Label', size=64, required=True, translate=True),
        'ttype': fields.selection(_get_fields_type, 'Field Type', size=64, required=True),
        'field_id': fields.many2one('ir.model.fields', 'product_id'),
        'translate':fields.boolean('Translate'),
        'required':fields.boolean('Required'),
        'selection': fields.char('Selection Options',size=256, help="List of options for a selection field, "
            "specified as a Python expression defining a list of (key, label) pairs. "
            "For example: [('blue','Blue'),('yellow','Yellow')]"),
        'relation': fields.char('Object Relation', size=64,
            help="For relationship fields, the technical name of the target model"),
        'relation_field': fields.char('Relation Field', size=64,
            help="For one2many fields, the field on the target model that implement the opposite many2one relationship"),
        'sequence': fields.integer('Sequence'),
    }

    _defaults = {
        'name':lambda * a:'x_',
    }

product_attributes()

class product_attributes_group(osv.osv):
    _name = 'product.attributes.group'
    _description = 'Product attributes group for product OpenERP module'
    
    def create_product_attributes_menu(self, cr, uid, ids, vals, context):
        if context is None:
            context = {}
        if type(ids) != list:
            ids = [ids]
            
        data_ids = self.pool.get('ir.model.data').search(cr, uid, [('name', '=', 'menu_products'), ('module', '=', 'product')])
        
        if data_ids:
            product_attributes_menu_id = self.pool.get('ir.model.data').read(cr, uid, data_ids[0], ['res_id'])['res_id']
            
        for attributes_group in self.browse(cr, uid, ids, context):
        
            menu_vals = {
                'name': attributes_group.name,
                'parent_id': product_attributes_menu_id,
                'icon': 'STOCK_JUSTIFY_FILL'
            }
            
            action_vals = {
                'name': attributes_group.name,
                'view_type':'form',
                'domain':"[('attribute_group_id', '=', %s)]" % attributes_group.id,
                'context': "{'attribute_group_id':%s}" % attributes_group.id,
                'res_model': 'product.product'
            }
            
            existing_menu_id = self.pool.get('ir.ui.menu').search(cr, uid, [('name', '=', attributes_group.name)])
            
            if len(existing_menu_id) > 0:
                raise osv.except_osv(_('Error !'), _('There are other menu same this group. Please, use another name'))
                
            else:
                action_id = self.pool.get('ir.actions.act_window').create(cr, uid, action_vals, context)
                menu_vals['action'] = 'ir.actions.act_window,%s' % (action_id)
                menu_id = self.pool.get('ir.ui.menu').create(cr, uid, menu_vals, context)
                values = {
                    'action_id': action_id,
                    'menu_id': menu_id,
                }
                super(product_attributes_group, self).write(cr, uid, ids, values, context)


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        id = super(product_attributes_group, self).create(cr, uid, vals, context)
        self.create_product_attributes_menu(cr, uid, [id], vals, context)
        return id


    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if type(ids) != list:
            ids = [ids]
            
        super(product_attributes_group, self).write(cr, uid, ids, vals, context)
        
        for attributes_group in self.browse(cr, uid, ids, context):
            menu_vals = {
                'name': attributes_group.name,
            }
            
            action_vals = {
                'name': attributes_group.name,
            }
            
            result = self.pool.get('ir.actions.act_window').write(cr, uid, attributes_group.action_id.id, action_vals, context)
            result = result and self.pool.get('ir.ui.menu').write(cr, uid, attributes_group.menu_id.id, menu_vals, context)
            
            if not result:
                raise osv.except_osv(_('Error !'), _('Error ocurring during saving'))

        return True


    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if type(ids) != list:
            ids = [ids]
        
        for attributes_group in self.browse(cr, uid, ids, context):
            result = self.pool.get('ir.actions.act_window').unlink(cr, uid, attributes_group.action_id.id, context)
            result = result and self.pool.get('ir.ui.menu').unlink(cr, uid, attributes_group.menu_id.id, context)
            
            result = result and super(product_attributes_group, self).unlink(cr, uid, attributes_group.id, context)
            
            if not result:
                raise osv.except_osv(_('Error !'), _('Error ocurring during deleting'))
            
        return True


    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'code': fields.char('Code', size=64, required=True, help='Attribute code, ex az09'),
        'product_att_ids': fields.many2many('product.attributes', 'product_attributes_rel', 'product_attributes_group_id', 'product_attributes_id', 'Products Attributes'),
        'menu_id': fields.many2one('ir.ui.menu', 'menu_id', readonly=True),
        'action_id': fields.many2one('ir.actions.act_window', 'action_id', readonly=True),
    }

product_attributes_group()
