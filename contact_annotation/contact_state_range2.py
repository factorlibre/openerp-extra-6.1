# -*- coding: utf-8 -*-
##############################################################################
#
#    school module for OpenERP
#    Copyright (C) 2010 Tecnoba S.L. (http://www.tecnoba.com)
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
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
from operator import attrgetter

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'
_ADMIN_USER=1

def incorpora_interval(intervals, interval):
    """
    Paràmetres:
      En intervals tindrem els intervals consecutius de temps ordenats de menor a major
    data amb diccionari de data inici, data fi, l'operació que té l'estat i la data d'efectivitat de l'estat.
    Date_to de l'interval anterior ha de ser igual al date_from del següent.
    Amb 'op':'+' l'estat hi és present i 'op':'-' no hi és present.
      En interval tindrem l'interval del nou estat que i la operació '+' o '-' que marcarà si volem afegir o treure l'estat. També en informarà de l'efectivitat de l'estat. L'anomenarem interval a tractar.
    Funció:
      Refà la llista d'intervals incorporant l'interval passat de la forma que s'explica en el codi
    Retorna:
      Una nova llista d'intervals booleans temporals ordenats amb data d'efectivitat
    """
    new_ranges=[] # la nova llista d'intervals que retornarem
    for range in intervals: # repassem els intervals un a un
        # demanem si l'interval a tractar toca en el temps a l'interval de la llista que repassem
        # a més, l'efectivitat ha de ser més actual, perquè si és més antiga, tampoc canviarem l'interval que repassem.
        if range['date_to']<=interval['date_from'] or range['date_from']>=interval['date_to'] or range['creation_date']>interval['creation_date']:
            # l'interval a tractar no toca l'interval que repassem, per tant l'afegim sense fer cap operació sobre ell
            # Noteu que es manté l'ordenació, la operació i l'efectivitat.
            new_ranges.append(range)
        else:
            # l'interval a tractar toca en el temps a aquest interval que repassem
            # anem a comprovar si queda algún tros de l'interval que repassem a l'esquerra del quin tractem...
            if interval['date_from']>range['date_from']:
                # doncs, si. Queda l'interval desde l'inici d'aquest interval que repassem fins a l'inici de l'interval a tractar que volem incloure
                new_ranges.append({
                    'date_from': range['date_from'],
                    'date_to': interval['date_from'],
                    'creation_date': range['creation_date'], 'paquet': range['paquet']})
            # afegim ara l'interval que queda en mig. L'inici serà el major entre l'inici de l'interval a repassar o l'inici de l'interval a tractar
            # Observeu:
            # - aquest interval sempre hi serà: hem comprovat que l'interval a tractar toca amb el quin repassem i té una efectivitat major
            # - aquest interval que sempre quedarà encadenat amb l'interval anterior:
            #    ; si existeix marge a l'esquerra entre l'interval que repassem i quin tractem, l'inici de l'interval que afegim serà l'inici del quin tractem que és el final que quin em afegit en la condició anterior
            #    ; si no existeix marge a l'esquerra, l'inici de l'interval serà el mateix que quin repassem
            #   així doncs, podem trobar directament l'inici d'aquest interval trobant el màxim entre els dos valors.
            # en el fi podem seguir el mateix raonament, però invertit
            # la operació serà la quina ens marqui l'interval i marcarem l'efectivitat de l'interval per següents inclusions d'altres intervals a tractar si es el cas
            new_ranges.append({
                'date_from': max(range['date_from'], interval['date_from']),
                'date_to': min(range['date_to'], interval['date_to']),
                'creation_date': interval['creation_date'], 'paquet': interval['paquet']})
            # anem a comprovar si queda algún tros de l'interval que repassem a la dreta del quin tractem...
            if interval['date_to']<range['date_to']:
                # doncs, si. Queda l'interval desde l'inici de l'interval a tractar que volem incloure fins a la fi d'aquest interval que repassem
                new_ranges.append({
                    'date_from': interval['date_to'],
                    'date_to': range['date_to'],
                    'creation_date': range['creation_date'], 'paquet': range['paquet']})
    return new_ranges

class contact_state_range2(osv.osv):
    _name='contact.state_range2'
contact_state_range2()

class contact_annotation(osv.osv):
    _name = 'contact.annotation'
    _inherit = 'contact.annotation'

    _columns = {
#        'contact_id' : fields.many2one('res.partner.contact', 'Contact', required=True, ondelete="cascade", select=True,),
#        'anno_type' : fields.many2one('contact.type_annotation', 'Type', required=True, ondelete="restrict", select=True, ),
#        'valid_from' : fields.datetime('Valid from',select=1,required=True,),
#        'valid_to' : fields.datetime('Valid to',select=1,required=True,),
#        'creation_date' : fields.datetime('Creation date', required=True, ),
        'state_range_ids' : fields.many2many('contact.state_range2','contact_annotation_state_range2','anno_id','state_range2_id',string='States',),
    }

    def _normalitza(self, cr, uid, tuples, valid_from, valid_to, context=None):
#        import pdb;pdb.set_trace()
        sr2_obj=super(contact_state_range2,self.pool.get('contact.state_range2'))
        for (contact_id,state_id) in tuples:
            # Fer buit
            ids_to_unlink=sr2_obj.search(cr, uid, [('lstate','=',state_id),('contact_id','=',contact_id),('datetime_from','>=',valid_from),('datetime_to','<=',valid_to)])
            sr2_obj.unlink(cr, uid, ids_to_unlink)
            ids_to_left=sr2_obj.search(cr, uid, [('lstate','=',state_id),('contact_id','=',contact_id),('datetime_from','<',valid_from),('datetime_to','>=',valid_from)])
            ids_to_right=sr2_obj.search(cr, uid, [('lstate','=',state_id),('contact_id','=',contact_id),('datetime_from','<=',valid_to),('datetime_to','>',valid_to)])
            ids_to_cut=dict.fromkeys(sr2_obj.search(cr, uid, [('lstate','=',state_id),('contact_id','=',contact_id),('datetime_from','<',valid_from),('datetime_to','>',valid_to)]),None)
            if ids_to_cut:
                for data in sr2_obj.read(cr, uid, ids_to_cut.keys(), ['datetime_from','datetime_to']):
                    ids_to_cut[data['id']]=(data['datetime_from'],data['datetime_to'])
            cr.execute("""
            SELECT a.id,a.valid_from,a.valid_to,a.creation_date,ats.op
            FROM contact_annotation AS a
                INNER JOIN contact_anno_type_state AS ats ON a.anno_type=ats.anno_type
                    AND ats.state_id=%(state_id)s
            WHERE a.contact_id=%(contact_id)s
                AND a.valid_from<%(datetime_to)s
                AND a.valid_to>%(datetime_from)s
            """,{'contact_id': contact_id, 'state_id': state_id, 'datetime_from': valid_from, 'datetime_to': valid_to})
            state_ranges=[{'date_from': valid_from, 'date_to': valid_to, 'creation_date': '0000-00-00', 'paquet': ('-',0)}]
            for (a_id,a_valid_from,a_valid_to,a_creation_date,ats_op) in cr.fetchall():
                state_ranges=incorpora_interval(state_ranges, {'date_from': a_valid_from, 'date_to': a_valid_to, 'creation_date': a_creation_date, 'paquet': (ats_op and '+' or '-',a_id),})
            # Ajunta intervals tocant
            new_list=[]
            counter=0
            for item in state_ranges:
                if not new_list:
                    new_list.append({'date_from': item['date_from'], 'date_to': item['date_to'], 'op': item['paquet'][0], 'annos': set([item['paquet'][1]])})
                else:
                    if new_list[counter]['op']==item['paquet'][0]:
                        new_list[counter]['date_to']=item['date_to']
                        new_list[counter]['annos'].add(item['paquet'][1])
                    else:
                        new_list.append({'date_from': item['date_from'], 'date_to': item['date_to'], 'op': item['paquet'][0], 'annos': set([item['paquet'][1]])})
                        counter+=1
            state_ranges=new_list
            if ids_to_cut:
                if state_ranges[0]['op']=='-':
                    sr2_obj.write(cr, uid, ids_to_cut.keys(), {'datetime_to': valid_from})
                    state_ranges.pop(0)
                    if state_ranges[-1]['op']=='+':
                        sr2_obj.create(cr, uid, {'contact_id': contact_id, 'lstate': state_id, 'datetime_from': state_ranges[-1]['date_from'],'datetime_to': ids_to_cut.values()[0][1]})
                        state_ranges.pop()
                    else:
                        sr2_obj.create(cr, uid, {'contact_id': contact_id, 'lstate': state_id, 'datetime_from': valid_to,'datetime_from': ids_to_cut.values()[0][1]})
                elif state_ranges[-1]['op']=='-':
                    sr2_obj.write(cr, uid, ids_to_cut.keys(), {'datetime_from': valid_to})
                    state_ranges.pop()
                    # state_ranges[0]['op']=='+'
                    sr2_obj.create(cr, uid, {'contact_id': contact_id, 'lstate': state_id, 'datetime_from': ids_to_cut.values()[0][0], 'datetime_to': state_ranges[0]['date_to']})
                    state_ranges.pop(0)
                elif len(state_ranges)>1:
                    ids_to_left+=ids_to_cut.keys()
                    ids_to_right.append( sr2_obj.create(cr, uid, {'contact_id': contact_id, 'lstate': state_id, 'datetime_from': valid_to,'datetime_from': ids_to_cut.values()[0][1]}) )
            if ids_to_left:
                if state_ranges and state_ranges[0]['op']=='+':
                    sr2_obj.write(cr, uid, ids_to_left, {'datetime_to': state_ranges[0]['date_to']})
                    state_ranges.pop(0)
                else:
                    sr2_obj.write(cr, uid, ids_to_left, {'datetime_to': valid_from})
            if ids_to_right:
                if state_ranges and state_ranges[-1]['op']=='+':
                    sr2_obj.write(cr, uid, ids_to_right, {'datetime_from': state_ranges[-1]['date_from']})
                    state_ranges.pop()
                else:
                    sr2_obj.write(cr, uid, ids_to_right, {'datetime_from': valid_to})
            for state_range in state_ranges:
                if state_range['op']=='+':
                    sr2_obj.create(cr, uid, {'contact_id': contact_id, 'lstate': state_id, 'datetime_from': state_range['date_from'], 'datetime_to': state_range['date_to'], 'annotation_ids': [(6,0,state_range['annos'])]})
                
    def normalitza(self, cr, uid, tuples, context=None):
        # susceptible de millora quan un mateix contacte i estat té intevals de temps coincidents
        for tupla in tuples:
            self._normalitza(cr, uid, [(tupla[0], tupla[1])], tupla[2], tupla[3], context=context)

    def normalitza_tot(self, cr, uid, context=None):
        cr.execute("""
        SELECT DISTINCT a.contact_id,ats.state_id FROM contact_annotation AS a
                INNER JOIN contact_anno_type_state AS ats ON a.anno_type=ats.anno_type
        """)
        self._normalitza(cr, 1, [(contact_id,state_id) for (contact_id,state_id) in cr.fetchall()], _MIN_DATETIME, _MAX_DATETIME, context=context)

    def _genera_tuples(self, cr, uid, ids, context=None):
        tuples=set()
        for obj in self.browse(cr, uid, ids):
            for data_state in obj.anno_type.data_states:
                tuples.add( (obj.contact_id.id, data_state.state_id.id, obj.valid_from, obj.valid_to) )
        return tuples
    
    def write(self, cr, uid, ids, vals, context=None):
        tuples=self._genera_tuples(cr, 1, ids, context=context)
        ret=super(contact_annotation, self).write(cr, uid, ids, vals, context=context)
        tuples.update(self._genera_tuples(cr, 1, ids, context=context))
        self.normalitza(cr, 1, tuples, context)
        return ret

    def create(self, cr, uid, vals, context=None):
        ret=super(contact_annotation, self).create(cr, uid, vals, context=context)
        tuples=self._genera_tuples(cr, 1, [ret], context=context)
        self.normalitza(cr, 1, tuples, context)
        return ret

    def unlink(self, cr, uid, ids, context=None):
        tuples=self._genera_tuples(cr, 1, ids, context=context)
        ret=super(contact_annotation, self).unlink(cr, uid, ids, context=context,)
        self.normalitza(cr, 1, tuples, context)
        return ret

contact_annotation()


class contact_state_range2(osv.osv):
    _name='contact.state_range2'

    def _annotation_for_state_range2(self, cr, uid, ids, field_name, args, context=None):
        ret={}.fromkeys(ids, '')
        for item in self.browse(cr, 1, ids):
            no_append=False
            abrs=set()
            ids_checked=self.pool.get('contact.annotation').check_perms(cr, uid, [x.id for x in item.annotation_ids], 'read', context=context)
            for anno in sorted(filter(lambda x: x.id in ids_checked,item.annotation_ids), key=attrgetter('creation_date'), reverse=True):
                for data_state in anno.anno_type.data_states:
                    if data_state.state_id.id==item.lstate.id and not data_state.op: no_append=True
                if not no_append: abrs.add(anno.anno_type.code or data.anno_type.name[0:5])
            ret[item.id]=','.join(abrs)
        return ret

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for state_range in self.browse(cr, uid, ids):
            ret.append( state_range.id, "%s, %s (%s - %s)" % (state_range.contact_id.name, state_range.lstate.code, state_range.datetime_from, state_range.datetime_to) )
            return ret
        
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        return []
    
    _columns={
        'annotation_ids' : fields.many2many('contact.annotation','contact_annotation_state_range2','state_range2_id','anno_id',string='Annotations',),
        'anno_ids_text': fields.function(_annotation_for_state_range2, type="char", method=True, string='Annotations',),
        'lstate': fields.many2one('contact.annotation.state','State',required=True,select=1,),
        'datetime_from': fields.datetime('From',select=1),
        'datetime_to': fields.datetime('To',select=1),
        'contact_id': fields.many2one('res.partner.contact','Contact',select=1,),
    }

    def get_states(self, cr, uid, state_ids=None, context=None):
        q="""
SELECT DISTINCT s.id FROM contact_annotation_state AS s
   INNER JOIN groups_contact_states_rel AS sgr ON s.id=sgr.state_id
   INNER JOIN res_groups_users_rel AS gu ON gu.gid=sgr.group_id
   WHERE gu.uid=%s"""
        p=[uid]
        if state_ids:
            q+=" AND s.id IN %s"
            p+=[tuple(state_ids)]
        cr.execute(q, p)
        return [x[0] for x in cr.fetchall()]

    def get_contacts_for_state(self, cr , uid, state_ids, contact_ids, context=None):
        ret={}
        query="""
SELECT DISTINCT cpf.contact_id,fs.state_id  FROM res_partner AS p, contact_partner_function AS cpf, function_and_state_rel AS fs
   WHERE p.user_id=%s AND cpf.partner_id=p.id AND fs.function_id=cpf.function_id"""
        params=[uid]
        if state_ids:
            query+=" AND fs.state_id IN %s"
            params.append( tuple(state_ids) )
        if contact_ids:
            query+=" AND cpf.contact_id IN %s"
            params.append( tuple(contact_ids) )
        cr.execute(query, params)
        for (contact_id,state_id) in cr.fetchall():
            if state_id not in ret: ret[state_id]=[]
            if contact_id not in ret[state_id]: ret[state_id].append(contact_id)
        return ret

    def _get_gids(self, cr, uid):
        cr.execute("select gid from res_groups_users_rel where uid=%s", (uid,))
        return [x[0] for x in cr.fetchall()]

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        state_ids=None
        contact_ids=None
        
        if not context: context={}
        
        # Volem només els estats dels contactes sobre els quin puguem crear anotacions de tipus context['anno_type-code'] (si existeix)
        if 'anno_type-code' in context:
            anno_type_codes=type(context['anno_type-code'])==str and [context['anno_type-code']] or context['anno_type-code']
            anno_type_ids=self.pool.get('contact.type_annotation').search(cr, uid, [('code','in',anno_type_codes)])
            if anno_type_ids:
                catga_ids=self.pool.get('contact.annotation_type.group_access').search(cr, uid, [('contact_type_annotation_id','in',anno_type_ids),('group_id','in',self._get_gids(cr, uid)),('perm_create','=',True)])
                if catga_ids:
                    anno_type_ids2=[type(x['contact_type_annotation_id'])==int and x['contact_type_annotation_id'] or x['contact_type_annotation_id'][0] for x in self.pool.get('contact.annotation_type.group_access').read(cr, uid, catga_ids, ['contact_type_annotation_id'])]
                    args+=[('lstate.id','in',self.pool.get('contact.anno_type.state').search(cr, uid, [('anno_type','in',[0]+anno_type_ids2),('op','=',True)]))]
                    map(anno_type_ids.remove,anno_type_ids2)
                if anno_type_ids:
                    fa_obj=self.pool.get('contact.annotation_type.function_access')
                    cpf_obj=self.pool.get('contact.partner.function')
                    functions_ids=[x['function_id'][0] for x in fa_obj.read(cr, uid, fa_obj.search(cr, uid, [('contact_type_annotation_id','in',anno_type_ids),('perm_create','=',True)]), ['function_id'])]
                    contact_ids2=[x['contact_id'][0] for x in cpf_obj.read(cr, uid, cpf_obj.search(cr, uid, [('partner_id.user_id','=',uid),('function_id','in',functions_ids)]), ['contact_id'])]
                    args+=[('contact_id.id','in',contact_ids2)]
        
        lstate_leafs=[] # States criteria
        contact_leafs=[] # Contacts criteria
        for toca in args:
            (field,op,expr)=toca
            field_parts=field.split('.',1)
            if field_parts[0]=='lstate':
                lstate_leafs+=[(len(field_parts)>1 and field_parts[1] or 'code',op,expr)]
            if field_parts[0]=='contact_id':
                contact_leafs+=[(len(field_parts)>1 and field_parts[1] or 'name',op,expr)]
        if lstate_leafs:
            state_ids=self.pool.get('contact.annotation.state').search(cr, uid, lstate_leafs)
        if contact_leafs:
            contact_ids=self.pool.get('res.partner.contact').search(cr, uid, contact_leafs)

        state_ids_to_args=self.get_states(cr, uid, state_ids, context=context)
        state_contact_to_args=self.get_contacts_for_state(cr, uid, state_ids, contact_ids, context=context)

        if state_contact_to_args: args.append('|')
        args+=[('lstate','in',state_ids_to_args)]
        if state_contact_to_args:
            state_contact_items=state_contact_to_args.items()
            for i in range(len(state_contact_items)):
                (state_id,contact_ids)=state_contact_items[i]
                if i<len(state_contact_items)-1: args.append('|')
                args+=['&',('lstate','=',state_id),('contact_id','in',contact_ids)]
        return super(contact_state_range2, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    _sql_constraints = []

    def get_contacts(self, cr , uid, context=None):
        if not context: context={}
        partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)], context=context)
        search_args= [('partner_id','in',partner_ids),]
        if 'function' in context:
            function_ids=self.pool.get('contact.annotation.function').search(cr, uid, [('name','ilike',context['function'])])
            search_args+= [('function_id','in',function_ids)]
        rel_ids=self.pool.get('contact.partner.function').search(cr, uid, search_args, context=context)
        return [item['contact_id'][0] for item in self.pool.get('contact.partner.function').read(cr, uid, rel_ids, ['contact_id'])]

    _order = "datetime_from"

contact_state_range2()

class contact_state_range2_norm(osv.osv_memory):
    _name='contact.state_range2_norm'
    
    def normalitza(self, cr, uid, ids, context=None):
        self.pool.get('contact.annotation').normalitza_tot(cr, uid, context=context)
        
contact_state_range2_norm()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
