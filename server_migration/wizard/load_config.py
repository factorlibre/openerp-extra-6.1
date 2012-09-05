# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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

from osv import osv, fields

class migration_wizard_config(osv.osv_memory):

    _name = "migration.wizard.config"
    _description = "Configuration Load"
    _inherit = "ir.wizard.screen"

    _columns = {
        'message': fields.char('Message', size=128, readonly=True),
    }

    def load_config(self, cr, uid, ids, context):

        model_obj = self.pool.get('ir.model')
        model_old_server_obj = self.pool.get('migration.old_model')
        field_old_server_obj = self.pool.get('migration.old_field')
        import_models_obj = self.pool.get('migration.import_models')
        model_fields_obj = self.pool.get('migration.model_fields')
        ir_model_fields_obj = self.pool.get('ir.model.fields')
        configuration_obj = self.pool.get('migration.configuration')

        for configuration in configuration_obj.browse(cr, uid, configuration_obj.search(cr, uid, [])):

            if configuration.model_object and configuration.model_object_old_server and configuration.sequence:
                model_id = model_obj.search(cr, uid, [('model', '=', configuration.model_object)])[0]
                model_old_server_ids = model_old_server_obj.search(cr, uid, [('model', '=', configuration.model_object_old_server)])
                if not model_old_server_ids:
                    raise osv.except_osv('Error !', 'Model ' + configuration.model_object_old_server + ' not present in old server')
                else: model_old_server_id = model_old_server_ids[0]
                current_import_model_id = import_models_obj.create(cr, uid, {'name': model_id, 'old_name':model_old_server_id, 'sequence': configuration.sequence})

            import_models_ids = import_models_obj.search(cr, uid, [('name.model', '=', configuration.field_object_name)])
            if not import_models_ids:
                raise osv.except_osv('Error !', 'Model ' + configuration.field_object_name + ' does not have an import configuration')
            else:
                import_models_id  = import_models_ids[0]
            field_id = ir_model_fields_obj.search(cr, uid, [('model', '=', configuration.field_object_name), ('name', '=', configuration.field_name)])[0]
            old_field_ids = field_old_server_obj.search(cr, uid, [
                ('model', '=', configuration.field_object_name_old_server), ('name', '=', configuration.field_name_old_server)])
            if not old_field_ids:
                raise osv.except_osv('Error !', 'Field ' + configuration.field_name_old_server + ' not present in old server')
            else: old_field_id = old_field_ids[0]
            model_field_id = model_fields_obj.create(cr, uid, {'name': field_id, 'old_name': old_field_id, 'import_model_id': import_models_id})

        return {
            'name': 'Import Models',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'migration.import_models',
            'view_id': False,
            'type': 'ir.actions.act_window',
            }

migration_wizard_config()
