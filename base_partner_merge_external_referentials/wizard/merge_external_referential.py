# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA 2011
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

from osv import fields, osv


class res_merge_external_referential(osv.osv_memory):
    _name = 'base.partner.merge.extref'
    _description = 'Methods for merge resources with external referentials'

    def has_an_external_ref(self, cr, uid, model, res_id, context):
        has_ref = False
        ids = self.pool.get('ir.model.data').search(cr, uid,
            [('model', '=', model),
             ('external_referential_id', '!=', False),
             ('res_id', '=', res_id),
             # we exclude the fake links, we consider we can merge these resources
             ('name', 'not like', 'mag_order'),
            ]
        )
        if ids:
            has_ref = True
        return has_ref

    def update_external_refs(self, cr, uid, model, new_res_id, old_res_ids, context):
        """ Update references to external referentials in ir_model_data
        """
        ir_model_data_obj = self.pool.get('ir.model.data')

        id_to_update = self.has_an_external_ref(cr, uid, model, old_res_ids[0], context) and old_res_ids[0] or \
                       self.has_an_external_ref(cr, uid, model, old_res_ids[1], context) and old_res_ids[1]

        if id_to_update:
            ids = ir_model_data_obj.search(cr, uid,
                                           [('res_id', '=', id_to_update),
                                            ('model', '=', model),
                                            ('external_referential_id', '!=', False)
                                           ],
                                           context=context)
            ir_model_data_obj.write(cr, uid, ids,
                                    {'res_id': new_res_id},
                                    context=context)

        # delete "fake" references on old resources
        ids = ir_model_data_obj.search(cr, uid,
                                       [('res_id', 'in', old_res_ids),
                                        ('model', '=', model),
                                        ('external_referential_id', '!=', False),
                                        ('name', 'like', 'mag_order')]
                                       )
        ir_model_data_obj.unlink(cr, uid, ids, context=context)
        return True

res_merge_external_referential()
