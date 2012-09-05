# -*- coding: utf-8 -*-
##############################################################################
#
#    school module for OpenERP
#    Copyright (C) 2010 Tecnoba S.L. (http://www.tecnoba.com)
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
#    Copyright (C) 2011 Zikzakmedia S.L. (http://www.zikzakmedia.com)
#       Jesús Martín Jiménez <jmargin@zikzakmedia.com> All Rights Reserved.
#
#    This file is a part of school module
#
#    school OpenERP module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    school OpenERP module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import osv, fields

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'
_ADMIN_USER=1

class contact_state(osv.osv):
    _name = 'contact.annotation.state'

contact_state()


class contact_type_and_state(osv.osv):
    _name = 'contact.anno_type.state'
    _columns = {
        'anno_type': fields.many2one('contact.type_annotation','Annotation type',ondelete='cascade',),
        'op' : fields.boolean('Operation',help='True add the state, False remove the state.'),
        'state_id': fields.many2one('contact.annotation.state','State',ondelete='cascade',)
    }

contact_type_and_state()


class contact_state(osv.osv):
    _name = 'contact.annotation.state'
    _columns = {
        'name': fields.char('Contact state name', size=64, translate=True, ),
        'code': fields.char('State code', size=20, required=True),
        'valid': fields.boolean('Valid',),
        'group_ids': fields.many2many('res.groups','groups_contact_states_rel','state_id','group_id',string='Groups',help='Groups that can view the status.'),
        'function_ids': fields.many2many('contact.annotation.function','function_and_state_rel','state_id','function_id',string='Functions',help="Partners can view the status over contact with these functions.")
    }

    _defaults = {
        'valid': lambda *a: True,
    }

    def _code_without_comas(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids):
            if item.code.find(',')>=0: return False
        return True

    _sql_constraints = [
        ('code_annotation_state_unique','unique(code)','Code must be unique'),
    ]
    _constraints = [
        (_code_without_comas,"The code must'n have comas",['code']),
    ]

    def name_get(self, cr, uid, ids, context=None):
        res=[]
        for item in self.browse(cr, uid, ids, context=context):
            if item.name:
                res.append( (item.id, item.name) )
            else:
                res.append( (item.id, item.code) )
        return res

    def _get_selection(self, cr, uid, context=None):
        ret=[]
        for item in self.read(cr, uid, self.search(cr, uid, [])):
            ret.append( (item['code'],item['name'] ) )
        return ret

    def create_if_not_exists(self, cr, uid, vals, context=None):
        ret=self.search(cr, uid, [('code','=',vals['code'])], context=context)
        if not ret:
            return self.create(cr, uid, vals, context=context)
        else:
            return ret[0]

contact_state()


class contact_type_annotation(osv.osv):
    _name = 'contact.type_annotation'
    _inherit = 'contact.type_annotation'

    def _states(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for anno_type in self.browse(cr, uid, ids,context=context):
            ret[anno_type.id]=''
            for data_state in anno_type.data_states:
                if len(ret[anno_type.id])>0: ret[anno_type.id]+=','
                if data_state.op: ret[anno_type.id]+='+'
                else: ret[anno_type.id]+='-'
                ret[anno_type.id]+=data_state.state_id.code
        return ret

    def normalize_states(self, cr, uid, states, context=None):
        ret_list=[]
        return ','+','.join(ret_list)+','

    def _save_states(self, cr, uid, id, name, value, fnct_inv, arg, context=None):
        if not context: context={}
        if context.get('_saving_states',False):
            return True
        ids_to_unlink=self.pool.get('contact.anno_type.state').search(cr, uid, [('anno_type','=',id)])
        self.pool.get('contact.anno_type.state').unlink(cr, uid, ids_to_unlink)
        for state in value.split(','):
            if not state: continue
            if state[0] not in ('-','+'): state='+'+state[1:]
            state_id=self.pool.get('contact.annotation.state').create_if_not_exists(cr, uid, {'code': state[1:]})
            self.pool.get('contact.anno_type.state').create(cr, uid, {'anno_type': id, 'op': (state[0]=='+'), 'state_id': state_id}, context={'_saving_states': True})
        return  True

    _columns = {
        'states' : fields.function(_states, fnct_inv=_save_states, method=True, string='States', type='char', size=150, help="States (letters from A-Z, words separates with comas, prefix - if retire state of annotations superseded).",
            store={
                'contact.type_annotation': ( lambda self, cr, uid, ids, context: ids , ['data_states'], 10),
                'contact.anno_type.state': ( lambda self, cr, uid, ids, context: [x['anno_type'][0] for x in self.read(cr, uid, ids, ['anno_type'])] , ['op','state_id'], 20),
            } ),
        'data_states': fields.one2many('contact.anno_type.state','anno_type',),
    }

contact_type_annotation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
