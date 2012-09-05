# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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
from sets import Set

import netsvc

DEBUG = False
LOGGER = netsvc.Logger()

class base_external_mapping_line(osv.osv):
    _name = 'base.external.mapping.line'
    _description = 'Base External Mapping Line'
    _rec_name = 'name_function'
    
    def _name_get_fnc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for mapping_line in self.browse(cr, uid, ids, context):
            res[mapping_line.id] = mapping_line.field_id or mapping_line.external_field
        return res
    
    _columns = {
        'name_function': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
    }

base_external_mapping_line()

class base_external_mapping(osv.osv):
    _name = 'base.external.mapping'
    _description = 'Base External Mapping'
    _rec_name = 'model_id'

    def get_oerp_to_external(self, cr, uid, code, ids=[], context=None, langs=[]):
        """From OpenERP values to External
            Search all mapping lines same code and calculated their values
            Return list with dictionary [{},{}]
            If not code or ids, return dicc blank
            @param code: name of mapping
            @param ids: ids get values
            @param many2many field: return a list with id m2m[]
        """

        res=[]

        fields_relationals = ['many2one','one2many','many2many']

        if code == '' or len(ids) == 0:
            LOGGER.notifyChannel(_("Base External Mapping"), netsvc.LOG_ERROR, _("Code or ids without value"))
            return res

        dj_mappline_ids = self.search(cr, uid, [('name','=',code)])
        if len(dj_mappline_ids) == 0:
            LOGGER.notifyChannel(_("Base External Mapping"), netsvc.LOG_ERROR, _("Mappline Code %s not found") % code)
            return res

        LOGGER.notifyChannel(_("Base External Mapping"), netsvc.LOG_INFO, _("Base External Mapping call %s") % code)
        LOGGER.notifyChannel(_("Base External Mapping"), netsvc.LOG_INFO, "IDS: %s" % ids)

        if not len(langs)>0:
            langs = self.pool.get('res.lang').search(cr, uid, [('active','=',True)])

        dj_mappline = self.browse(cr, uid, dj_mappline_ids[0])

        dj_mappline_line_ids = self.pool.get('base.external.mapping.line').search(cr, uid, [('mapping_id','=',dj_mappline_ids[0]),('active','=',True),'|',('type','=','out'),('type','=','in_out')])

        mappline_rules = []
        for dj_mappline_line_id in dj_mappline_line_ids:
            mappline_rules_values = {}
            dj_mappline_line = self.pool.get('base.external.mapping.line').browse(cr, uid, dj_mappline_line_id, context)
            if dj_mappline_line.type == 'out' or dj_mappline_line.type == 'in_out':
                mappline_rules_values['field_id'] = dj_mappline_line.field_id.name
                mappline_rules_values['translate'] = dj_mappline_line.translate
                mappline_rules_values['external_field'] = dj_mappline_line.external_field
                mappline_rules_values['out_function'] = dj_mappline_line.out_function
                mappline_rules_values['ttype'] = dj_mappline_line.field_id.ttype
            mappline_rules.append(mappline_rules_values)

        for data_id in ids:
            values_data = {}
            values_model = self.pool.get(dj_mappline.model_id.model).browse(cr, uid, data_id, context)

            values_data['id'] = data_id
            
            for mappline_rule in mappline_rules:
                field =  mappline_rule['field_id']
                if mappline_rule['translate']:
                    for lang in langs:
                        language = self.pool.get('res.lang').browse(cr, uid, lang)
                        if language.code != 'en_US':
                            trans = self.pool.get('ir.translation').search(cr, uid, [('lang', '=', language.code),('name','=',dj_mappline.model_id.model+','+field),('res_id','=',data_id)])
                            if len(trans) > 0:
                                translation = self.pool.get('ir.translation').browse(cr, uid, trans[0])
                                trans_value = translation.value
                            else:
                                trans_value = getattr(values_model, field)
                                if trans_value is False:
                                    trans_value = ''
                        else:
                            trans_value = getattr(values_model, field)
                            if trans_value is False:
                                trans_value = ''
                        values_data[mappline_rule['external_field']+'_'+language.code[:2]]= trans_value
                else:
                    if mappline_rule['out_function']:
                        localspace = {"self":self,"cr":cr,"uid":uid,"ids":ids,"context":context}
                        exec mappline_rule['out_function'] in localspace
                        value = localspace['value'] if 'value' in localspace else None
                    else:
                        if mappline_rule['ttype'] in fields_relationals:
                            if mappline_rule['ttype'] == 'many2many': #m2m fields, create list
                                value = []
                                values = getattr(values_model, field)
                                for val in values:
                                    value.append(val.id)
                            else:
                                value = getattr(values_model, field).id
                        else:
                            value = getattr(values_model, field)

                        if mappline_rule['ttype'] == 'char' and value == False:
                            value = ''

                    if mappline_rule['ttype'] == 'boolean' and value == False: #force add this false
                        values_data[mappline_rule['external_field']]= False
                    if value:
                        values_data[mappline_rule['external_field']]= value

            res.append(values_data)

        if DEBUG:
            LOGGER.notifyChannel(_("Base External Mapping"), netsvc.LOG_INFO, _("%s") % res)

        return res

    def get_external_to_oerp(self, cr, uid, code, id, values={}, context=None):
        """
        From External values to OpenERP
        Get dicc and process values
        @param code: str
        @param id: int
        @param values: dicc
        :return vals dicc values recalculated
        """

        external_mappings = self.search(cr, uid, [('name','=',code)])
        if not (external_mappings)>0:
            return False

        vals = {}
        external_mapping = self.browse(cr, uid, external_mappings[0])
        for mapping_line in external_mapping.mapping_ids:
            if mapping_line.external_field in values and (mapping_line.type == 'in_out' or mapping_line.type == 'in') and mapping_line.active == True:
                if mapping_line.in_function:
                    localspace = {"self":self,"cr":cr,"uid":uid,"id":id,"values":values[mapping_line.external_field],"context":context}
                    exec mapping_line.in_function in localspace
                    value = localspace['value']
                else:
                    value = values[mapping_line.external_field]
                #force type value (float, int, bool) (default is str)
                if mapping_line.external_type == 'float':
                    try:
                        value = float(value)
                    except:
                        pass
                if mapping_line.external_type == 'int':
                    try:
                        value = int(value)
                    except:
                        pass
                if mapping_line.external_type == 'bool':
                    if value == '1':
                        value = True
                    else:
                        value = False
                vals[mapping_line.field_id.name] = value

        return vals

    def exclude_uptade(self, cr, uid, code, values={}, context=None):
        """
        Exclude some values dicc (remove dicc values)
        @param code: str
        @param values: dicc
        :return vals dicc values recalculated
        """

        external_mappings = self.search(cr, uid, [('name','=',code)])
        if not (external_mappings)>0:
            return False

        exclude_lines = []
        for line in self.browse(cr, uid, external_mappings[0]).mapping_ids:
            if line.update:
                exclude_lines.append(line.field_id.name)

        for line in exclude_lines:
            if line in values:
                del values[line]

        return values

    _columns = {
        'name': fields.char('Code', size=64, required=True),
        'model_id': fields.many2one('ir.model', 'OpenERP Model', required=True, select=True, ondelete='cascade'),
        'model':fields.related('model_id', 'model', type='char', string='Model Name'),
        'mapping_ids': fields.one2many('base.external.mapping.line', 'mapping_id', 'Mappings Lines'),
        'state' : fields.selection([('draft', 'Draft'),('done', 'Done')],'State',required=True,readonly=True),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

    def create(self, cr, uid, vals, context=None):
        dj_external_mapping_ids = self.pool.get('base.external.mapping').search(cr, uid, [('name','ilike',vals['name'])])
        if len(dj_external_mapping_ids) > 0:
            raise osv.except_osv(_('Error !'), _("Another External Mapping have same code!"))
        vals['state'] = 'done'
        return super(base_external_mapping, self).create(cr, uid, vals, context)

base_external_mapping()

class base_external_mapping_line(osv.osv):
    _inherit = 'base.external.mapping.line'

    def _check_mapping_line_name(self, cr, uid, ids):
        for mapping_line in self.browse(cr, uid, ids):
            if (not mapping_line.field_id) and (not mapping_line.external_field):
                return False
        return True
    
    _columns = {
        'mapping_id': fields.many2one('base.external.mapping', 'External Mapping', select=True, ondelete='cascade'),
        'field_id': fields.many2one('ir.model.fields', 'OpenERP Field', select=True, ondelete='cascade', required=True,domain="[('model_id', '=', parent.model_id),('ttype','!=','binary')]"),
        'external_field': fields.char('External Field', size=32, required=True),
        'type': fields.selection([('in_out', 'External <-> OpenERP'), ('in', 'External -> OpenERP'), ('out', 'External <- OpenERP')], 'Type', required=True),
        'external_type': fields.selection([('str', 'String'), ('bool', 'Boolean'), ('int', 'Integer'), ('float', 'Float')], 'External Type', required=True),
        'translate': fields.boolean('Translate', help='Check this option to export fields with locale sufix. Example: name_es'),
        'active': fields.boolean('Active'),
        'update': fields.boolean('Exclude Update', help='When update data (write), this field is excluded'),
        'sequence': fields.integer('Sequence', help="Is the order that you want for the columns field in the file"),
        'in_function': fields.text('Import in OpenERP Mapping Python Function'),
        'out_function': fields.text('Export from OpenERP Mapping Python Function'),
    }
    
    _default = {
        'type' : lambda * a: 'in_out',
        'active': 1,
    }
    
    _constraints = [
        (_check_mapping_line_name, "Error ! Invalid Mapping Line Name: Field and External Field cannot be both null", ['parent_id'])
    ]
    
    _order = 'field_id desc'

base_external_mapping_line()
