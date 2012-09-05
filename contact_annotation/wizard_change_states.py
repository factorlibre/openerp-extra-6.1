# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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


from osv import osv, fields
from operator import attrgetter
import time
import wizard
import pooler
from tools.translate import _

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'


class contact_planning_change_states(osv.osv):
    _name='contact.planning_change_states'
contact_planning_change_states()


class open_wizard(wizard.interface):
    def _open_wizard(self, cr, uid, data, context=None):
        if not context: context={}
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'contact_annotation', 'contact_planning_change_states_list_act')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id], [])[0]
        views={}
        for (view_id,view_mode) in result['views']: views[view_mode]=view_id
        result['views'] = [(views['form'],'form')]

        obj=pooler.get_pool(cr.dbname).get('contact.planning_change_states')
        vals=obj.default_get(cr, uid, obj.fields_get(cr, uid, context=context).keys(), context={'active_ids': data['ids']})
        res_id=obj.create(cr, uid, vals, context={'active_ids': data['ids']})

        result['res_id'] = res_id
        result['target'] = 'new'
        return result

    states = {
          'init': {
                'actions': [],
                'result': {'type': 'action',
                           'action': _open_wizard,
                           'state':'end'}
          },
    }

open_wizard('contact_open_change_states')


class contact_state_range(osv.osv):
    _name='contact.state_range'

    def _annotation_for_state_range(self, cr, uid, ids, field_name, args, context=None):
        ret={}
        for item in self.read(cr, uid, ids, ['lstate','contact_id','datetime_from','datetime_to'], context=context):
            lstate_id = item['lstate']
            if type(lstate_id) not in (long,int):
                lstate_id=lstate_id[0]
            contact_id = item['contact_id']
            if type(contact_id) in (list,tuple):
                contact_id = contact_id[0]
            anno_type_ids = self.pool.get('contact.type_annotation').search(cr, uid, [('data_states.state_id','=',lstate_id)])
            anno_ids = self.pool.get('contact.annotation').search(cr, uid, [('anno_type','in',anno_type_ids),('contact_id','=',contact_id),('valid_to','>',item['datetime_from']),('valid_from','<',item['datetime_to'])], )
            anno_ids_ret = []
            abrs = set()
            no_append = False
            for data in sorted(self.pool.get('contact.annotation').browse(cr, uid, anno_ids), key=attrgetter('creation_date'), reverse=True):
                for data_state in data.anno_type.data_states:
                    if data_state.state_id.id == lstate_id and not data_state.op: no_append=True
                if not no_append:
                    anno_ids_ret.append(data.id)
                    abrs.add(data.anno_type.code or data.anno_type.name[0:5])
            ret[item['id']]={'annotation_ids': anno_ids_ret, 'anno_ids_text': ','.join(abrs)}
        return ret

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for state_range in self.browse(cr, uid, ids):
            ret.append( state_range.id, "%s, %s (%s - %s)" % (state_range.contact_id.name, state_range.lstate.code, state_range.datetime_from, state_range.datetime_to) )
            return ret

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        return []
    
    _columns={
        'annotation_ids': fields.function(_annotation_for_state_range, type='one2many', obj='contact.annotation', method=True, string='Annotations', multi='annos',),
        'anno_ids_text': fields.function(_annotation_for_state_range, type="char", method=True, string='Annotations', multi='annos',),
        'planning_id': fields.many2one('contact.planning_change_states','Planning',ondelete='cascade',),
        'lstate': fields.many2one('contact.annotation.state','State',),
        'datetime_from': fields.datetime('From'),
        'datetime_to': fields.datetime('To'),
        'contact_id': fields.many2one('res.partner.contact','Contact',),
    }

    def create(self, cr, uid, vals, context=None):
        if not context: context={}
        ret=super(contact_state_range, self).create(cr, uid, vals, context=context)
        return ret
contact_state_range()

class contact_planning_change_states(osv.osv):
    _name='contact.planning_change_states'

    def _anno_types_which_change_set(self, cr, uid, state_id=None, informer_id=None, contact_id=None, context=None):
        ret=set()
        if not contact_id or not state_id: return ret
        query="""
SELECT at.id FROM contact_type_annotation AS at
  LEFT JOIN contact_anno_type_state AS ats ON at.id=ats.anno_type
  LEFT JOIN contact_annotation_type_group_access AS atga ON at.id=atga.contact_type_annotation_id
  LEFT JOIN res_groups_users_rel AS gur ON gur.gid=atga.group_id AND gur.uid=%s
WHERE ats.state_id=%s AND ats.op='f' AND gur.uid IS NOT NULL
        """
        cr.execute(query, (uid,state_id,))
        for (at_id,) in cr.fetchall(): ret.add(at_id)

        partner_rel_from_user=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)])
        partner_rel=partner_rel_from_user+[informer_id]

        query="""
SELECT at.id FROM contact_type_annotation AS at
  LEFT JOIN contact_anno_type_state AS ats ON at.id=ats.anno_type
  LEFT JOIN contact_annotation_type_function_access AS atfa ON at.id=atfa.contact_type_annotation_id
  LEFT JOIN contact_partner_function AS pf ON atfa.function_id=pf.function_id AND pf.partner_id in %s AND pf.contact_id=%s
WHERE ats.state_id=%s AND ats.op='f' AND pf.id IS NOT NULL
        """
        cr.execute(query, (tuple(partner_rel),contact_id,state_id,))
        for (at_id,) in cr.fetchall(): ret.add(at_id)
        return ret

    def _domain_anno_types(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for planning in self.browse(cr, uid, ids, context=context):
            dummy=set()
            initiated=False
            for state_range in planning.state_ranges:
                anno_type_ids=self._anno_types_which_change_set(cr, uid, state_id=state_range.lstate.id, informer_id=planning.user_id.id, contact_id=state_range.contact_id.id, context=context)
                if not initiated:
                    dummy.update(anno_type_ids)
                    initiated=True
                else:
                    dummy.intersection_update(anno_type_ids)
            ret[planning.id]=list(dummy)
        ret2={}
        for (key,value) in ret.items():
            if not value: ret2[key]='0'
            else: ret2[key]=','.join(map(str,value))
        return ret2

    def _return_nothing(self, cr, uid, ids, field_name, arg, context=None):
        return dict( (id, []) for id in ids)

    def _create_state_ranges(self, cr, uid, id, name, value, fnct_inv_arg, context=None):
        # Per comprovar que navega per registres que realment existeixen s'ha de fer primer un search que retornarà una llista dels ids de la taula
        #state_range2_ids = self.pool.get(('contact.state_range2').search(cr, uid, [('id', '=', id)])
        print value, context
        for (type,operation,ids) in value:
            # I després s'hauria d'obligar a que navegués pels registres que existeixen, i no pas pels que se li pasa amb el paràmetre ids=value[2]
            # for state_range2 in self.pool.get('contact.state_range2').browse(cr, uid, state_range2_ids):
            for state_range2 in self.pool.get('contact.state_range2').browse(cr, uid, ids):
                # Perquè sinó, intenta navegar per un registre (ids) que no existeix i peta
                self.pool.get('contact.state_range').create(cr, uid, {'lstate': state_range2.lstate.id, 'contact_id': state_range2.contact_id.id , 'planning_id': id, 'datetime_to': state_range2.datetime_to, 'datetime_from': state_range2.datetime_from, })
        return True

    _columns={
        'name': fields.char('Name',size=50,),
        'date': fields.datetime('Date'),
        'state_ranges': fields.one2many('contact.state_range','planning_id','Planning',),
        'state_ranges2': fields.function(_return_nothing, fnct_inv=_create_state_ranges, type='many2many', obj='contact.state_range2', string='Planning',method=True,),
        'user_id': fields.many2one('res.users','User',ondelete='cascade',readonly=True,),
        'state': fields.selection((('new','New'),('ready','Ready'),('sended','Sended'),('executed','Executed'),),'State',readonly=True,),
        'anno_type': fields.many2one('contact.type_annotation','Type to register',required=False,readonly=True,states={'ready': {'readonly': False,},'sended': {'readonly': False,},}),
        'domain_anno_types': fields.function(_domain_anno_types, type='char', method=True, ),
        'comment': fields.text('Comment'),
        'permanent': fields.boolean('Permanent',),
    }

    def _change_state_ranges(self, cr, uid, ids, state_ranges, context=None):
        return {'domain': {'anno_type': ('id','in',[]),}, }
       
    def _default_range_states2(self, cr, uid, context=None):
        ret=[]
        if not context: context={}
#        for item in self.pool.get('contact.state_range2').browse(cr, uid, context.get('active_ids',[])
#            ret.append( {'id': item.id, 'datetime_from': item.datetime_from, 'datetime_to': item.datetime_to, 'lstate': (item.lstate.id, item.lstate.name), 'contact_id': (item.contact_id.id, item.contact_id.name), [{'contact_id': (x.id,x.name), 'anno_type': } in ] } )
        return context.get('active_ids',[])

    _defaults={
        'date': lambda *a:time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': lambda *a: 'new',
        'name': lambda *a: _('Planing')+' '+time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, context: uid,
        'state_ranges2': _default_range_states2,
    }

    def create(self, cr, uid, vals, context=None):
        state_ranges2=vals.pop('state_ranges2', [])
        ret=super(contact_planning_change_states, self).create(cr , uid, vals, context=context)
        return ret

    def write(self, cr, uid, ids, vals, context=None):
        state_ranges2=vals.pop('state_ranges2', [])
        ret=super(contact_planning_change_states, self).write(cr , uid, ids, vals, context=context)
        return ret

    def action_ready_planning(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'ready',}, context=context)
        return True

    def action_execute_planning(self, cr, uid, ids, context=None):

        self.write(cr, uid, ids, {'state': 'executed'}, context=context)
        for planning in self.browse(cr,uid,ids,context=context):
            data={}
            for state_range in planning.state_ranges:
                # @type data dict
                key=state_range.contact_id.id
                if key not in data:
                    data[key]={'from': state_range.datetime_from, 'to': state_range.datetime_to, }
                else:
                    if data[key]['from']>state_range.datetime_from: data[key]['from']=state_range.datetime_from
                    if data[key]['to']<state_range.datetime_to: data[key]['to']=state_range.datetime_to
            report_date=planning.date
            if planning.permanent: report_date=_MAX_DATETIME
            if not planning.anno_type:
                return {'warning': {'anno_type': ('Error!','Annotation type is needed.')}}
            else:
                for (contact_id,range) in data.items():
                    partner_ids=self.pool.get('res.partner').search(cr,uid,[('user_id','=',planning.user_id.id)])
                    self.pool.get('contact.annotation').create(cr, uid, {'contact_id': contact_id, 'informer': partner_ids and partner_ids[0] or False,'anno_type': planning.anno_type.id, 'valid_from': range['from'], 'valid_to': range['to'], 'comment': planning.comment, 'creation_date': report_date})
        return {'type': 'ir.actions.act_window_close'}


contact_planning_change_states()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

