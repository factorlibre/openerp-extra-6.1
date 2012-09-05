# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
#                       Raimon Esteve <resteve@zikzakmedia.com>
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
from tools.translate import _

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'attribute_group_id': fields.many2one('product.attributes.group', 'Attribute'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        result = super(osv.osv, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar)
        if view_type == 'form':
            if context.get('attribute_group_id', False):

                product_attributes_group = self.pool.get('product.attributes.group').browse(cr, uid, context.get('attribute_group_id'))

                field_names = []
                view_part = ''

                #Sequence fields
                prod_attributes = [{'sequence':pa.sequence, 'id':pa.id} for pa in product_attributes_group.product_att_ids]
                fields = sorted(prod_attributes, key=lambda k: k['sequence'])

                pfields = []
                for field in fields:
                    pfields.append(field['id'])

                #Create new view - fields
                for pfield in pfields:
                    product_attribute = self.pool.get('product.attributes').browse(cr, uid, pfield)
                    if str(product_attribute.name).startswith('x_'):
                        field_names.append(product_attribute.name)
                        if product_attribute['ttype'] == 'text':
                            view_part+="<newline/><separator colspan='4' string='%s'/>" % product_attribute.field_description
                        view_part+= '<field name="%s"' % product_attribute.name
                        if product_attribute.ttype == 'text':
                            view_part+=" colspan='4' nolabel='1' " 
                        view_part+= '/>\n'

                result['fields'].update(self.fields_get(cr, uid, field_names, context))

                result['arch'] = result['arch'].decode('utf8').replace('<page string="product_attributes_placeholder"/>', '<page string="'+product_attributes_group.name+'" attrs="{\'invisible\':[(\'attribute_group_id\',\'=\',False)]}">'+view_part+'</page>')
            else:
                result['arch'] = result['arch'].replace('<page string="product_attributes_placeholder"/>', "")

        return result

product_product()
