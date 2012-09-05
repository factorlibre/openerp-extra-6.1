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
from tools.translate import _

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'

class groups_group(osv.osv):
    _name = 'groups.group'

groups_group()


class groups_participation(osv.osv):
    _name = 'groups.participation'

groups_participation()


class groups_group_assignation(osv.osv):
    _name = 'groups.group_assignation'
    _columns =  {
        'group_id' : fields.many2one('groups.group','Group', required=True,
            select=1, ondelete='cascade',),
        'participation_id' : fields.many2one('groups.participation', 'Participation',
            required=True, select=1, ondelete='cascade'),
        'datetime_from' : fields.datetime('Begining', select=1,),
        'datetime_to' : fields.datetime('End', select=1,),
    }

    _sql_constraints = [('dates_ok','CHECK (datetime_to>=datetime_from)','Date to is minor than date from'),]

    def _assignation_in_domain(self, cr, uid, ids):
        data=self.read(cr, uid, ids, ['group_id','participation_id','datetime_from','datetime_to'], context={'withoutBlank': False})
        gids=set()
        for item in data:
            if item['datetime_from']!=item['datetime_to']: gids.add(item['group_id'])
        domains=self.pool.get('groups.group')._domain_assignations(cr, uid, list(gids))
        if domains:
            for item in data:
                group_id=item['group_id']
                participation_id=item['participation_id']
                if (group_id not in domains) or (domains[group_id] is None): continue
                # No participation in domain group
                if not participation_id in domains[group_id]: return False
                interval_into=(item['datetime_from'],item['datetime_to'])
                ret=False
                for interval_domain in domains[group_id][participation_id]:
                    if interval_into[0]>=interval_domain[0] and interval_into[1]<=interval_domain[1]: ret=True
                # No inclusive intervals in domain group for participation_id
                if not ret: return False
        return True

    _constraints = [
        (_assignation_in_domain, 'Assignation dates out of domain of the parents or parent assignation does not exist yet!', ['datetime_from', 'datetime_to']),
        ]

    def unlink(self, cr, uid, ids, context=None):
        if not ids: return True
        if context is None:
            context = {}
        # Reduim interval a zero. Write ja esborra els intervals buits o modifica els intervals laterals
        for ga in self.browse(cr, uid, ids, context={'withoutBlank': False }):
            if ga.datetime_from!=ga.datetime_to:
                self.redueixo(cr, uid, ga, None, ga.datetime_from)
                # Ja haurem comprovat la concurrencia en la reducció
                if '__last_update' in context: context['__last_update'].pop('groups.group_assignation,%s' % ga.id, False)
        super(groups_group_assignation, self).unlink(cr, uid, ids, context=context)
        return True

    def _cut(self, cr, uid, group_id, participation_id, ldatetime):
        ids_a_retallar=set()
        # retallem ga de la mateixa participacio i amb un grup que formi part de la classificació 
        gdata=self.pool.get('groups.group').read(cr, uid, [group_id], ['parent_ids','classification'])[0]
        if gdata['classification']:
            ids_a_retallar.update(self.search(cr, uid, [('participation_id','=',participation_id),('group_id.parent_ids','in',gdata['parent_ids']),('group_id.classification.id','=',gdata['classification'][0]),('datetime_from','<',ldatetime),('datetime_to','>',ldatetime)]))
        ids_a_retallar.update(self.search(cr, uid, [('participation_id','=',participation_id),('group_id.parent_ids','=',group_id),('datetime_from','<',ldatetime),('datetime_to','>',ldatetime)]))
        groups_to_revise_cut=set()
        for gadata in self.read(cr, uid, list(ids_a_retallar), ['group_id','datetime_to'], context={'withoutBlank': False}):
            group_id2=gadata['group_id']
            if type(group_id2)==type([]): group_id2=gadata['group_id'][0]
            groups_to_revise_cut.add(group_id2)
            super(groups_group_assignation, self).create(cr, uid, {'group_id': group_id2, 'participation_id': participation_id, 'datetime_from': ldatetime, 'datetime_to': gadata['datetime_to']})
        super(groups_group_assignation, self).write(cr, uid, list(ids_a_retallar), {'datetime_to': ldatetime})
        for group_to_revise_cut in groups_to_revise_cut:
            self._cut(cr, uid, group_to_revise_cut, participation_id, ldatetime)

    def _create_empty(self, cr, uid, group_id, participation_id, ldatetime):
        id=super(groups_group_assignation, self).create(cr, uid, {'group_id': group_id, 'participation_id': participation_id, 'datetime_from': ldatetime, 'datetime_to': ldatetime})
        children=self.pool.get('groups.group').search(cr, uid, [('parent_ids','=',group_id),('creation','>',0)])
        classifications=[]
        for gdata in self.pool.get('groups.group').read(cr, uid, children, ['classification','creation']):
            if not gdata['classification'] or gdata['classification'] not in classifications:
                self._create_empty(cr, uid, gdata['id'], participation_id, ldatetime)
                if gdata['classification']: classifications.append(gdata['classification'])
        return id

    def create(self, cr, uid, vals, context=None):
        if not context: context = {}
        if 'datetime_from' not in vals: vals['datetime_from']=_MIN_DATETIME
        if 'datetime_to' not in vals: vals['datetime_to']=_MAX_DATETIME
        if not vals['datetime_from'] or vals['datetime_from']<_MIN_DATETIME: vals['datetime_from']=_MIN_DATETIME
        if not vals['datetime_to'] or vals['datetime_to']>_MAX_DATETIME: vals['datetime_to']=_MAX_DATETIME
        if vals['datetime_to']==vals['datetime_from']: return True
        
        # Hi ha segments que toquin amb el mateix grup i participació?
        ga_ids=self.search(cr, uid, [('group_id','=',vals['group_id']),('participation_id','=',vals['participation_id']),('datetime_from','<=',vals['datetime_to']),('datetime_to','>=',vals['datetime_from'])],None,None,'datetime_from')
        if ga_ids:
            # Aprofitem el primer i fem un write modificant-lo, si cal
            dummy=self.read(cr, uid, [ga_ids[0],ga_ids[-1]],['datetime_from','datetime_to'], context={'withoutBlank': False})
            primer=dummy[0]
            darrer=dummy[-1]
        else:
            self._cut(cr, uid, vals['group_id'], vals['participation_id'], vals['datetime_from'])
            id_empty=self._create_empty(cr, uid, vals['group_id'], vals['participation_id'], vals['datetime_from'])
            primer={'id': id_empty, 'datetime_from': vals['datetime_from'], 'datetime_to': vals['datetime_from'], }
            darrer=primer
            # ara cal crear
        self.write(cr, uid, primer['id'], {'datetime_from': min(primer['datetime_from'],vals['datetime_from']), 'datetime_to': max(darrer['datetime_to'],vals['datetime_to'])})
        return primer['id']

    def read(self, cr, uid, ids, fields, context=None, load='_classic_write'):
        if not fields: fields=[]
        if not context: context={}
        ret=super(groups_group_assignation, self).read(cr, uid, ids, fields, context=context, load=load)
        # @type context dict
        if context.get('withoutBlank', True):
            # @type ret list
            for item in ret:
                if 'datetime_from' in item:
                    if item['datetime_from']==_MIN_DATETIME: item['datetime_from']=''
                if 'datetime_to' in item:
                    if item['datetime_to']==_MAX_DATETIME: item['datetime_to']=''
        return ret

    def amplio(self, cr ,uid, ga, datetime_from, datetime_to, context=None):
        ret=True
        if not context: context={}
        # primer modifico assignacions de classificacions laterals, després els meus limits i després modifico els fills
        if ga.group_id.classification and context.get('tracta_classificacions', True):
            # cerco assignacions de classificacions per l'esquerra            
            ids_parcials=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('id','!=',ga.id),('group_id.classification.id','=',ga.group_id.classification.id),('participation_id','=',ga.participation_id.id)])
            ids_laterals_a_esborrar=[]
            new_context=context.copy().update({'tracta_classificacions': False});
            if datetime_from:
                ids_laterals_a_esborrar+=self.search(cr, uid, [('id','in',ids_parcials),('datetime_to','<=',ga.datetime_from),('datetime_from','>',datetime_from)])
                id_lateral_a_reduir_per_esquerra=self.search(cr, uid, [('id','in',ids_parcials),('id','not in',ids_laterals_a_esborrar),('datetime_to','<=',ga.datetime_from),('datetime_to','>',datetime_from)])
                self.write(cr, uid, id_lateral_a_reduir_per_esquerra, {'datetime_to': datetime_from}, context=new_context)
            if datetime_to:
                ids_laterals_a_esborrar+=self.search(cr, uid, [('id','in',ids_parcials),('datetime_from','>=',ga.datetime_to),('datetime_to','<',datetime_to)])
                id_lateral_a_reduir_per_dreta=self.search(cr, uid, [('id','in',ids_parcials),('id','not in',ids_laterals_a_esborrar),('datetime_from','>=',ga.datetime_to),('datetime_from','<',datetime_to)])
                self.write(cr, uid, id_lateral_a_reduir_per_dreta, {'datetime_from': datetime_to}, context=new_context)
            self.unlink(cr, uid, ids_laterals_a_esborrar, context=new_context)
        # ja tindria buits els laterals d'assignacions de la classificacio
        # ara amplio els limits de l'assignació actual
        if datetime_from:
            datetime_from_ant=ga.datetime_from
            # modifico limit per l'esquerra
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_from': datetime_from})
            # modifico fills
            id_fills_a_ampliar_esquerra=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_from','=',datetime_from_ant)])
            self.write(cr, uid, id_fills_a_ampliar_esquerra, {'datetime_from': datetime_from})
        if datetime_to:
            datetime_to_ant=ga.datetime_to
            # modifico limit per la dreta
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_to': datetime_to})
            # modifico fills
            id_fills_a_ampliar_dreta=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_to','=',datetime_to_ant)])
            self.write(cr, uid, id_fills_a_ampliar_dreta, {'datetime_to': datetime_to})
        return ret

    def redueixo(self, cr ,uid, ga, datetime_from, datetime_to, context=None):
        if not context: context={}
        ret=True
        # primer modifico els fills, després els meus límits i finalment acomodo les assignacions de classificacions laterals sempre que estiguin dins del seus dominis
        if datetime_from:
            ids_interiors_a_esborrar=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_from','>',ga.datetime_from),('datetime_to','<=',datetime_from)])
            self.unlink(cr, uid, ids_interiors_a_esborrar , context=context)
            id_fill_a_reduir_esquerra=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_from','<',datetime_from),('datetime_to','>',ga.datetime_from)])
            self.write(cr, uid, id_fill_a_reduir_esquerra, {'datetime_from': datetime_from})
            # TODO: Per poder treure la limitació d'assignacions no coincidents en els pares cal comprovar que la reducció dels fills sigui necessaria per la reducció del domini conjunt
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_from': datetime_from})
        if datetime_to:
            ids_interiors_a_esborrar=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_from','>=',datetime_to),('datetime_from','<',ga.datetime_to)])
            self.unlink(cr, uid, ids_interiors_a_esborrar , context=context)
            id_fill_a_reduir_dreta=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.id),('participation_id','=',ga.participation_id.id),('datetime_to','>',datetime_to),('datetime_from','<',ga.datetime_to)])
            self.write(cr, uid, id_fill_a_reduir_dreta, {'datetime_to': datetime_to})
            # TODO: Per poder treure la limitació d'assignacions no coincidents en els pares cal comprovar que la reducció dels fills sigui necessaria per la reducció del domini conjunt
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_to': datetime_to})
        if ga.group_id.classification and context.get('tracta_classificacions', True):
            new_context=context.copy().update({'tracta_classificacions': False});
            # cerco assignacions de classificacions per l'esquerra
            if datetime_from:
                ga_classificacio_a_ampliar_esquerra=self.search(cr, uid, [('id','!=',ga.id),('participation_id','=',ga.participation_id.id),('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('group_id.classification.id','=',ga.group_id.classification.id),('datetime_to','=',ga.datetime_from)])
                self.write(cr, uid, ga_classificacio_a_ampliar_esquerra, {'datetime_to': datetime_from}, context=new_context)
            if datetime_to:
                ga_classificacio_a_ampliar_dreta=self.search(cr, uid, [('id','!=',ga.id),('participation_id','=',ga.participation_id.id),('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('group_id.classification.id','=',ga.group_id.classification.id),('datetime_from','=',ga.datetime_to)])
                self.write(cr, uid, ga_classificacio_a_ampliar_dreta, {'datetime_from': datetime_to}, context=new_context)
        return ret

    def write(self, cr, uid, ids, vals, context=None):
        ret=True
        if not ids: return ret # No cal fer res
        if type(ids)!=type([]): ids=[ids]
        
        # Preparació de paràmetres amb valors per defecte
        if context is None:
            context = {}
        if not vals: vals={}
        if 'datetime_from' in vals:
            if not vals['datetime_from'] or vals['datetime_from']<_MIN_DATETIME:
                vals['datetime_from']=_MIN_DATETIME
        if 'datetime_to' in vals:
            if not vals['datetime_to'] or vals['datetime_to']>_MAX_DATETIME:
                vals['datetime_to']=_MAX_DATETIME

        if vals.has_key('datetime_from') or vals.has_key('datetime_to'):
            for ga in self.browse(cr, uid, ids, context={'withoutBlank': False }):
                # casos
                if vals.get('datetime_from',ga.datetime_from)==vals.get('datetime_to',ga.datetime_to): # esborra
                    self.unlink(cr, uid, [ga.id], context=context)
                elif vals.get('datetime_from',ga.datetime_from)>ga.datetime_to or vals.get('datetime_to',ga.datetime_to)<ga.datetime_from:
                    self.unlink(cr, uid, [ga.id], context=context)
                    self.create(cr, uid, {'participation_id': ga.participation_id.id, 'group_id': ga.group_id.id, 'datetime_from': vals['datetime_from'], 'datetime_to': vals['datetime_to']}, context=context)
                else:
                    datetime_from_plus=None;datetime_to_plus=None
                    datetime_from_minus=None;datetime_to_minus=None
                    if vals.get('datetime_from',ga.datetime_from)<ga.datetime_from: datetime_from_plus=vals['datetime_from'] # amplia per la dreta
                    if vals.get('datetime_from',ga.datetime_from)>ga.datetime_from: datetime_from_minus=vals['datetime_from'] # redueix per la dreta
                    if vals.get('datetime_to',ga.datetime_to)>ga.datetime_to: datetime_to_plus=vals['datetime_to']# amplia per l'esquerra
                    if vals.get('datetime_to',ga.datetime_to)<ga.datetime_to: datetime_to_minus=vals['datetime_to'] # redueix per l'esquerra
                    ret&=self.amplio(cr, uid, ga, datetime_from_plus, datetime_to_plus)
                    ret&=self.redueixo(cr, uid, ga, datetime_from_minus, datetime_to_minus)
        for key in ('group_id','participation_id','datetime_from','datetime_to'):
            if key in vals: vals.pop(key)
        if vals:
            ret&=super(groups_group_assignation, self).write(cr, uid, ids, vals, context=context)
        return ret

groups_group_assignation()


class groups_participation(osv.osv):
    _name = 'groups.participation'

    def _get_groups(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for obj in self.browse(cr, uid, ids):
            reti=set()
            retxt=[]
            for obj2 in sorted(obj.assignation_ids, key=lambda assig: assig.group_id.name):
                reti.add(obj2.group_id.id)
                retxt.append(obj2.group_id.name)
            ret[obj.id]={'group_ids': list(reti), 'group_txt': ','.join(retxt)}
        return ret

    def _search_by_group(self, cr, uid, obj, name, args, context=None):
        ga_obj=self.pool.get('groups.group_assignation')
        ga_ids=ga_obj.search(cr, uid, [('group_id.name',op,value) for (namex,op,value) in args if namex==name])
        return [('id','in',[x['participation_id'] for x in ga_obj.read(cr, uid, ga_ids, ['participation_id'])])]

    _columns = {
        'name' : fields.char('Ref',size=32),
        'participant' : fields.many2one('res.partner.contact', 'Participant',
            required=True, ondelete="cascade", select=1,
            help="The contact of the participation."),
        'assignation_ids' : fields.one2many('groups.group_assignation', 'participation_id','Assignations',),
        'group_ids' : fields.function(_get_groups, fnct_search=_search_by_group, arg=None, type='many2many', obj='groups.group', method=True, string="Groups", multi='groups',),
        'group_txt' : fields.function(_get_groups, arg=None, type='char', method=True, string="Groups with assignation", multi='groups',),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context:
            obj.pool.get('ir.sequence').get(cr, uid, 'groups.ref.participation'),
    }

    def groups_in_interval(self, cr, uid, ids, date_from=_MIN_DATETIME, date_to=_MAX_DATETIME, context=None):
        """
        Retorna un diccionari amb claus els identificadors de les participacions
        contingudes en la llista del paràmetre ids. Els valors són una llista de
        diccionaris amb dades sobre els grups amb assignacions per la participació
        identificada amb la clau dins el periode determinat pels paràmetres
        date_from i date_to. La llista de grups es troba ordenada per prioritat
        éssent el grup amb prioritat més alta el quin és primer.
        """
        if not ids: return {}
        res={}
        for id in ids: res[id]=[]
        if ids:
            query="""
            SELECT ga.participation_id,ga.datetime_from,ga.datetime_to,g.id AS gid,g.priority
            FROM groups_group_assignation AS ga
            INNER JOIN groups_group AS g ON ga.group_id=g.id
            WHERE ga.participation_id in %(part_ids)s
                AND ga.limit_from<'%(date_to)s'
                AND ga.limit_to>'%(date_from)s'
            ORDER BY g.priority,ga.datetime_from DESC
            """ % {'part_ids': tuple(ids+[0]),'date_from': date_from, 'date_to': date_to, }
            cr.execute(query)
            for (part_id,datetime_from,datetime_to,group_id,priority) in cr.fetchall():
                if part_id not in res: res[part_id]=[]
                res[part_id]+=[{'group_id': group_id,'datetime_from': datetime_from,'datetime_to': datetime_to,'priority':priority}]
        return res

    def copy(self, cr, uid, id, default={}, context=None):
        group_name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({
            'name': _('%s (copy)') % group_name,
            'assignation_ids': False,
        })
        return super(groups_participation, self).copy(cr, uid, id, default, context)

groups_participation()

class groups_classification(osv.osv):
    _name = 'groups.classification'
    
    _columns = {
        'name' : fields.char('Name',size=50,),
        'group_ids' : fields.one2many('groups.group','classification',string='Groups',),
    }
groups_classification()

class groups_group(osv.osv):
    _name = 'groups.group'

    def _participants(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for id in ids: ret[id]=[]
        query='select group_id,participation_id from groups_group_assignation where group_id in %s'
        cr.execute(query, (tuple(ids,),))
        for (gid,pid) in cr.fetchall(): ret[gid].append(pid)
        return ret

    def _get_group_ids_and_our_children(self, cr, uid, ids, context=None):
        if not context: context={}
        context.setdefault('_get_group_ids_and_our_children_proof', 0)
        if not ids or context['_get_group_ids_and_our_children_proof']>100: return []
        context['_get_group_ids_and_our_children_proof']+=1
        ret=set(ids)
        ids2=self.search(cr, uid, [('parent_ids','in',ids)])
        ret.update(self._get_group_ids_and_our_children(cr, uid, ids2, context=context))
        return list(ret)

    def _compute_name2(self, cr, uid, ids, field_name, arg, context=None):
        if not context: context={}
        # creem cache si no es troba definida
        context.setdefault('iji', {})
        ret={}
        
        ids1=self.search(cr, uid, [('id','in',ids),('parent_ids','not in',ids)]) # només els pares
        parents={}
        ids_to_read_parents=[]
        for id in self.search(cr, uid, [('children_ids','in',ids1)]):
            if id not in context['iji']: ids_to_read_parents.append(id)
            else: parents[id]=context['iji'][id]
        for data in self.read(cr, uid, ids_to_read_parents, ['name2'], context=context):
            parents[data['id']]=data['name2']
        
        for data in self.read(cr, uid, ids1, ['name','parent_ids']):
            parents_name=[parents.get(id,'') or '' for id in data.get('parent_ids',[])]
            if len(parents_name):
                ret[data['id']] = '+'.join(parents_name)+'/'+data['name']
            else:
                ret[data['id']] = data['name']
            context['iji'][data['id']]=ret[data['id']]
            
        children_ids=self.search(cr, uid, [('parent_ids','in',ids1)])
        if children_ids:
            ret.update( self._compute_name2(cr, uid, children_ids, field_name, arg, context=context) )

        # Tot i només tractar els pares, la informació dels fills s'anirà completant amb la recursió
        return ret
        
    _columns = {
        'name' : fields.char('Name', size=100, required=True, select=1, help="The group name."),
        'name2' : fields.function(_compute_name2, type='char', size=200, method=True, string='Complete name', select=1, store={'groups.group': (_get_group_ids_and_our_children, ['name','parent_ids'], 10 ),}),
        'parent_ids' : fields.many2many('groups.group','groups_parent_groups_rel','son','father',string='Parents',required=False,
            select=1, help="The parent groups."),
        'assignation_ids' : fields.one2many('groups.group_assignation','group_id','Assignations'),
        'children_ids' : fields.many2many('groups.group','groups_parent_groups_rel','father','son',string='Children',select=1,help="The subgroups of the group."),
        'classification' : fields.many2one('groups.classification',string='Classification',select=1,),
        'priority' : fields.integer('Priority',required=True,),
        'participants' : fields.function(_participants, method=True, type='one2many',relation='groups.participation'),
        'creation' : fields.integer('Auto creation', required=True,),
    }

    _defaults = {
        'creation': lambda *a: 0,
        'priority': lambda *a: 0,
    }
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct father from groups_parent_groups_rel where son in ('+
                ','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    def _check_classification(self, cr, uid, ids):
        cr.execute("select g.id from groups_group as g inner join groups_parent_groups_rel as gr on g.id=gr.son where classification is not null and g.id in %s group by g.id having count(*)<>1", (tuple(ids),) )
        if cr.fetchall(): return false
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive groups.', ['parent_ids']),
        (_check_classification, 'When a group is member of a classification, it must have only one parent.',['classification'])
    ]

    def _domain_assignations(self, cr, uid, ids, context=None):
        def _inclou_interval_en_llista(llista, interval):
            ret=[]
            (dtf0,dtt0)=interval
            afegit=False
            for (dtf,dtt) in llista:
                if dtt<dtf0:
                    ret.append( (dtf,dtt) )
                elif dtt0<dtf:
                    if not afegit:
                        afegit=True
                        ret.append( (dtf0, dtt0 ) )
                    ret.append( (dtf,dtt) )
                else:
                    dtf0=min(dtf,dtf0)
                    dtt0=max(dtt,dtt0)
            if not afegit: ret.append( (dtf0, dtt0 ) )
            return ret

        ret={}
        domains={}
        for item in self.browse(cr, uid, ids, context={'withoutBlank': False}):
            id=item.id
            ret[id]={}
            if item.parent_ids:
                for parent in item.parent_ids:
                    pid=parent.id
                    if not pid in domains: # per estalviar-nos cercar dominis de pares iguals
                        dict={}
                        for assignation in parent.assignation_ids:
                            key=assignation.participation_id.id
                            if not key in dict: dict[key]=[]
                            dict[key].append( (assignation.datetime_from,assignation.datetime_to) )
                        domains[pid]=dict
                    for (key,value) in domains[pid].items():
                        if key not in ret[id]: ret[id][key]=[]
                        for interval in value:
                            ret[id][key]=_inclou_interval_en_llista(ret[id][key], interval)
            else:
                ret[id]=None # No parent, no domain
        return ret

    def copy(self, cr, uid, id, default={}, context=None):
        group_name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({
            'name': _('%s (copy)') % group_name,
            'assignation_ids': False,
        })
        return super(groups_group, self).copy(cr, uid, id, default, context)

groups_group()
