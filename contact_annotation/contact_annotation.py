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


from osv import osv, fields, orm
from tools.translate import _
from datetime import datetime

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'
_ADMIN_USER=1

class contact_type_annotation(osv.osv):

    _name = 'contact.type_annotation'
    
contact_type_annotation()


class contact_annotation_type_group_access(osv.osv):

    _name = 'contact.annotation_type.group_access'

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for item in self.browse(cr, uid, ids, context=context):
            ret.append((item.id, "%s - %s" % (item.contact_type_annotation_id.name, group_id.name)))
        return ret

    _columns = {
        'contact_type_annotation_id': fields.many2one('contact.type_annotation', 'Type', required=True),
        'group_id': fields.many2one('res.groups', 'Group'),
        'perm_read': fields.boolean('Read Access'),
        'perm_write': fields.boolean('Write Access'),
        'perm_create': fields.boolean('Create Access'),
        'perm_unlink': fields.boolean('Delete Permission'),
    }

    _sql_constraints = [
        ('anno_type_group_access_unique','unique(contact_type_annotation_id,group_id)','Each annotation type must have only one group.'),
    ]

contact_annotation_type_group_access()


class contact_annotation_function(osv.osv):

    _name = 'contact.annotation.function'
    _columns = {
        'name': fields.char('Function name', translate=True, size=64,),
        'code': fields.char('Code',size=10,),
        'ref' : fields.char('Ref',size=20,),
    }
    
contact_annotation_function()


class contact_partner_function(osv.osv):

    _name = 'contact.partner.function'
    _log_access = True

    # TODO?: Access rules:
    #    Manager group can access all registers
    #    Others users can access contact or partner related with user or created by user.

    def _name_get(self, cr, uid, ids, context=None):
        ret=[]
        for obj in self.browse(cr, uid, ids):
            ret.append(obj.id, "%s - %s - %s" % (obj.contact_id.name, obj.partner_id.name, function.name))
        return ret
        
    _columns = {
        'contact_id': fields.many2one('res.partner.contact','Contact',select=True,),
        'partner_id': fields.many2one('res.partner','Partner',select=True,),
        'function_id': fields.many2one('contact.annotation.function','Function',select=True,),
    }

contact_partner_function()


class contact_annotation_type_function_access(osv.osv):

    _name = 'contact.annotation_type.function_access'

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for item in self.browse(cr, uid, ids, context=context):
            ret.append((item.id, "%s - %s" % (item.contact_type_annotation_id.name, function_id.name)))
        return ret

    _columns = {
        'contact_type_annotation_id': fields.many2one('contact.type_annotation', 'Type', required=True),
        'function_id': fields.many2one('contact.annotation.function', 'Function'),
        'perm_read': fields.boolean('Read Access'),
        'perm_write': fields.boolean('Write Access'),
        'perm_create': fields.boolean('Create Access'),
        'perm_unlink': fields.boolean('Delete Permission'),
    }

    _sql_constraints = [
        ('anno_type_function_access_unique','unique(contact_type_annotation_id,function_id)','Each annotation type must have only one function.'),
    ]

contact_annotation_type_function_access()


class contact_type_annotation(osv.osv):

    _name = 'contact.type_annotation'
    _columns = {
        'name' : fields.char('Name', size=30, translate=True, ),
        'code' : fields.char('Code', size=5, ),
        'perms_functions' : fields.one2many('contact.annotation_type.function_access','contact_type_annotation_id',string='Informer functions',help='Perms for informer function over contact to create that annotation type.'),
        'perms_groups' : fields.one2many('contact.annotation_type.group_access', 'contact_type_annotation_id', string='Groups', help='Group which users could create and modify that annotation type.',),
    }

    def _get_gids(self, cr, uid):
        cr.execute("select gid from res_groups_users_rel where uid=%s", (uid,))
        return [x[0] for x in cr.fetchall()]

    def get_type_annotations(self, cr, uid, contact_ids=None, task='read', context=None):
        ret=set()
        if task not in ('read','write','create','unlink'): task='read'
        if type(contact_ids)!=type([]): contact_ids=[]
        if type(contact_ids)!=type({}): context={}
        group_access_ids=self.pool.get('contact.annotation_type.group_access').search(cr, uid, [('group_id','in',self._get_gids(cr, uid)),('perm_'+task,'=',True)])
        ret.update( self.search(cr, uid, [('perms_groups','in',group_access_ids)], context=context) )
        if contact_ids:
            functions={}
            partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)], context=context)
            rel_ids=self.pool.get('contact.partner.function').search(cr, uid, [('partner_id','in',partner_ids),('contact_id','in',contact_ids),], context=context)
            for item in self.pool.get('contact.partner.function').read(cr, uid, rel_ids, ['contact_id','function_id'] ):
                if item['function_id'][0] not in functions: functions[item['function_id'][0]]=[]
                functions[item['function_id'][0]].append(item['contact_id'][0])
            functions_to_search=[]
            for (function_id, contact_ids2) in functions.items():
                if len(contact_ids)==len(contact_ids2):
                    functions_to_search.append(function_id)
            function_access_ids=self.pool.get('contact.annotation_type.function_access').search(cr, uid, [('function_id','in',functions_to_search),('perm_'+task,'=',True)])
            ret.update (self.search(cr, uid, [('perms_functions','in',function_access_ids+[0])] , context=context) )
        return list(ret)

contact_type_annotation()


class contact_subtype_annotation(osv.osv):

    _name = 'contact.subtype_annotation'

    _columns = {
        'name' : fields.char('Name', size=60, translate=True, ),
        'code' : fields.char('Code', size=5, ),
        'anno_type' : fields.many2one('contact.type_annotation', 'Type', required=True, select=1,),
    }

contact_subtype_annotation()


class contact_annotation(osv.osv):

    _name = 'contact.annotation'

    def name_get(self, cr, uid, ids, context={}):
        res=[]
        for item in self.browse(cr, uid, ids):
            res.append((item.id, '%s,%s,%s-%s' % (item.contact_id.name,item.anno_type.name,item.valid_from,item.valid_to)))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        contact_ids=self.pool.get('res.partner.contact').search(cr, uid, [('name','ilike',name)], limit=limit, context=context)
        type_ids=self.pool.get('contact.type_annotation').search(cr, uid, [('name','ilike',name)], limit=limit, context=context)
        ids=self.search(cr, uid, ['|',('contact_id','in',contact_ids),('anno_type','in',type_ids)], limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    _columns = {
        'user_id': fields.many2one('res.users', 'Responsible'),
        'partner_id': fields.related('contact_id','job_ids','address_id','partner_id',type='many2one',\
                         relation='res.partner', string='Main Employer'),
        'contact_id' : fields.many2one('res.partner.contact', 'Contact', required=True, ondelete="cascade", select=True,),
        'anno_type' : fields.many2one('contact.type_annotation', 'Type', required=True, ondelete="restrict", select=True, ),
        'anno_subtype' : fields.many2one('contact.subtype_annotation', 'Subtype', required=False, domain="[('anno_type','=',anno_type)]", ondelete="restrict", select=True,),
        'valid_from' : fields.datetime('Valid from',select=1,required=True,),
        'valid_to' : fields.datetime('Valid to',select=1,required=True,),
        'comment' : fields.text('Commment'),
        'informer' : fields.many2one('res.partner', 'Informer', ondelete="restrict", select=True, ),
        'creation_date' : fields.datetime('Creation date', required=True, ),
        'domain_anno_types' : fields.function(lambda self,cr,uid,ids,field_name,args,context: {}.fromkeys(ids, '0'), type='char', method=True, string='Domain Annotation Types'),
    }

    _order="creation_date desc"
    
    _sql_constraints=[('date_interval_ok','CHECK (valid_to>valid_from)','Date from must to be minor than date to'),]

    def _default_domain_anno_types(self, cr, uid, context=None):
        if not context: context={}
        ret=[]
        if 'force_anno_types' in context:
            ret=self.pool.get('contact.type_annotation').search(cr, uid, [('code','in',context.get('force_anno_types',[]))])
        else:
            contact_ids=None
            if 'default_contact_id' in context:
                contact_ids=[context['default_contact_id']]
            ret=self.pool.get('contact.type_annotation').get_type_annotations(cr, uid, contact_ids, task='create', context=context)
        ret2='0'
        if ret: ret2=','.join(map(str,ret))
        return ret2

    def _default_informer(self, cr, uid, context=None):
        partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)])
        return partner_ids and partner_ids[0] or False

    _defaults={
        'creation_date' : lambda *a: datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id' : lambda self,cr,uid,context: uid,
        'domain_anno_types' : _default_domain_anno_types,
        'informer' : _default_informer,
        }

    def check_perms(self, cr, uid, ids, task, context=None):
        if not ids or task not in ('read','write','unlink','create'): return []
        user=self.pool.get('res.users').browse(cr, uid, uid)
        group_ids=[x.id for x in user.groups_id]+[0]
        partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)])+[0]
        query="""
            SELECT DISTINCT a.id FROM contact_annotation AS a
                     INNER JOIN contact_type_annotation AS ta ON a.anno_type=ta.id
                     LEFT JOIN contact_partner_function AS cpf ON cpf.contact_id=a.contact_id AND cpf.partner_id IN %%s
                     LEFT JOIN contact_annotation_type_group_access AS ga ON ta.id=ga.contact_type_annotation_id AND ga.perm_%s='t' AND group_id IN %%s
                     LEFT JOIN contact_annotation_type_function_access AS fa ON ta.id=fa.contact_type_annotation_id AND fa.perm_%s='t' AND fa.function_id=cpf.function_id
            WHERE a.id IN %%s AND (ga.id IS NOT NULL OR fa.id IS NOT NULL OR ( (a.user_id=%%s OR a.informer IN %%s) AND '%s'='read'))
        """ % (task,task,task)
        cr.execute(query, (tuple(partner_ids), tuple(group_ids), tuple(ids), uid, tuple(partner_ids), ) )
        return [x[0] for x in cr.fetchall()]
        
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ret=super(contact_annotation, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=False)
        ret=self.check_perms(cr, uid, ret, 'read', context=context)
        if count: return len(ret)
        return ret
        
    def write(self, cr, uid, ids, vals, context=None):
#        ids_with_perms=self.check_perms(cr, uid, ids, 'write', context=context)
#        if [x for x in ids if x not in ids_with_perms]: raise orm.except_orm(_('Error'), _('Not granted!'))
        fields_updatables=['comment','anno_subtype']
        for key in vals.keys():
            if key not in fields_updatables: del vals[key]
        if not vals: return True
        return super(contact_annotation, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        ret=super(contact_annotation, self).create(cr, uid, vals, context=context)
        ids_with_perms=self.check_perms(cr, uid, [ret], 'create', context=context)
        if ret not in ids_with_perms:
            raise orm.except_orm(_('Error'), _('Not granted!'))
        return ret

    def unlink(self, cr, uid, ids, context=None):
        ids_with_perms=self.check_perms(cr, uid, ids, 'unlink', context=context)
        for x in ids:
            if x not in ids_with_perms:
                raise orm.except_orm(_('Error'), _('Not granted!'))
        return super(contact_annotation, self).unlink(cr, uid, ids, context=context,)

    def read(self, cr, uid, ids, fields=None, context=None, load=None):
        ids_with_perms=self.check_perms(cr, uid, ids, 'read', context=context)
        for x in ids:
            if x not in ids_with_perms:
                raise orm.except_orm(_('Error'), _('Not granted!'))
        return super(contact_annotation, self).read(cr, uid, ids, fields=fields, context=context)
       
    def on_change_contact_id(self, cr, uid, ids, contact_id, anno_type, context=None):
        if not context: context={}
        ret=[]
        if 'force_anno_types' in context:
            ret=self.pool.get('contact.type_annotation').search(cr, uid, [('code','in',context.get('force_anno_types',[]))])
        else:
            contact_ids=contact_id
            if type(contact_ids) in (int,long): contact_ids=[contact_ids]
            ret=self.pool.get('contact.type_annotation').get_type_annotations(cr, uid, contact_ids, task='create', context=context)
        ret2=['0']
        if ret: ret2=','.join(map(str,ret))
        if anno_type and anno_type in ret:
            return {'value': {'domain_anno_types' : ret2, },}
        else:
            return {'value': {'domain_anno_types' : ret2, 'anno_type': False},}

    def on_change_anno_type(self, cr, uid, ids, context=None):
        return {'value': {'anno_subtype' : False, },}

contact_annotation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
