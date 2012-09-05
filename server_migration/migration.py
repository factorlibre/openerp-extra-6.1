# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008-2009 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
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

from osv import osv,fields
import time
import pooler
import traceback, sys
import xmlrpclib
from mx import DateTime
from mx.DateTime import now
from tools.translate import _
import netsvc

class except_orm(Exception):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.args = (name, value)

class server_migration_config(osv.osv):
    _name = "migration.server.connect_config"
    _description = "Remote server configuration"

    _columns = {
        'name': fields.char('User name', size=16, required=True),
        'password': fields.char('Password', size=16, required=True),
        'db_name': fields.char('Data Base', size=32, required=True),
        'host': fields.char('Address', size=16, required=True),
        'port': fields.integer('Port'),
    }
    _defaults = {
        'port': lambda *a: 8069,
    }
server_migration_config()

class migration_old_model(osv.osv):
    _name = 'migration.old_model'

    _columns = {
        'name': fields.char('Object Name', size=64, translate=True, required=True),
        'model': fields.char('Object', size=64, required=True, select=1),
        'field_id': fields.one2many('migration.old_field', 'model_id', 'Fields', required=True),
    }
    
migration_old_model()


class migration_old_field(osv.osv):
    _name = 'migration.old_field'

    _columns = {
        'name': fields.char('Name', required=True, size=64, select=1),
        'model': fields.char('Object Name', size=64, required=True),
        'relation': fields.char('Object Relation', size=64),
        'relation_field': fields.char('Relation Field', size=64),
        'model_id': fields.many2one('migration.old_model', 'Object ID', required=True, select=True, ondelete='cascade'),
        'field_description': fields.char('Field Label', required=True, size=256),
        'ttype': fields.selection([('binary','binary'),('boolean','boolean'),('char','char'),('date','date'),('datetime','datetime'),\
            ('float','float'),('integer','integer'),('integer_big','integer_big'),('many2many','many2many'),('many2one','many2one'),('one2many','one2many'),('reference','reference'),\
            ('selection','selection'),('text','text'),('string','string')], 'Field Type', size=64, required=True),
        'selection': fields.char('Field Selection',size=128),
        'required': fields.boolean('Required'),
        'readonly': fields.boolean('Readonly'),
        'size': fields.integer('Size'),
    }
    
migration_old_field()

class migration_import_models(osv.osv):
    _name = "migration.import_models"
    _order = 'sequence'

    def _get_sequence(self, cr, uid, context={}):
        ids = self.search(cr, uid, [])
        sequence = 0
        for r in self.browse(cr, uid, ids, context=context):
            if r.sequence >= sequence:
                sequence = r.sequence
        sequence += 1
        return sequence

    def _check_model_fields(self, cr, uid, ids):
        for rec in self.browse(cr, uid, ids):
            model_fields_ids = map(int, rec.name.field_id)
            required_model_fields_ids = self.pool.get('ir.model.fields').search(cr, uid, [('id','in',model_fields_ids),('required','=',True)])
            req_fields_ids = []
            field_ids = map(int, rec.field)
            result = ''
            if not field_ids:
                return result
            added_field_ids = []
            for field in self.pool.get('migration.model_fields').browse(cr, uid, field_ids, {}):
                if field.name.model_id and field.name.model_id.id!=rec.name.id or field.name.id in added_field_ids:
                    self.pool.get('migration.model_fields').unlink(cr, uid, field.id)
                added_field_ids.append(field.name.id or field.old_name.id)
            for req_field_id in required_model_fields_ids:
                if req_field_id not in added_field_ids:
                    req_fields_ids.append(req_field_id)
            if req_fields_ids:
                field_names = ''
                req_fields = self.pool.get('ir.model.fields').read(cr, uid, req_fields_ids, ['name'])
                for field_name in req_fields:
                    field_names += field_name['name']+', '
                result = field_names[:len(field_names)-2]
        return result

    def get_fields(self, cr, uid, ids, context={}):
        import_model = self.browse(cr, uid, ids[0], context=context)
        field_ids = map(int, import_model.name.field_id)
        import_model_field_ids = []
        for field in import_model.field:
            import_model_field_ids.append(field.name.id)
        for field_id in field_ids:
            if field_id not in import_model_field_ids:
                self.pool.get('migration.model_fields').create(cr, uid, {'import_model_id': import_model.id, 'name': field_id})
        '''
        if import_model.name and not import_model.field:
            fields = [(0,0,{'name':x}) for x in field_ids]
            self.write(cr, uid, ids, {'field':fields})
        '''
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        vals=vals.copy()
        res = super(migration_import_models, self).write(cr, uid, ids, vals, context=context)
        if not vals.has_key('message'):
            if isinstance(ids, (int, long)):
                ids = [ids]
            check_res = self._check_model_fields(cr, uid, ids)
            if check_res:
                self.write(cr, uid, ids, {'message': 'Were not added required field(s): '+check_res})
            else:
                self.write(cr, uid, ids, {'message': ''})
        return res

    def create(self, cr, uid, vals, context={}):
        if not context:
            context={}
        vals=vals.copy()
        c = context.copy()
        c['novalidate'] = True
        result = super(migration_import_models, self).create(cr, uid, vals, c)
        check_res = self._check_model_fields(cr, uid, [result])
        if check_res:
            self.write(cr, uid, [result], {'message': 'Were not added required field(s): '+check_res})
        else:
            self.write(cr, uid,  [result], {'message': ''})
        return result

    _columns = {
        'name': fields.many2one('ir.model', 'Model', required=True),
        #'old_name':fields.char('Model name on the old server', size=64),
        'old_name': fields.many2one('migration.old_model', 'Model on the old server'),
        'sequence': fields.integer('Sequence'),
        'field': fields.one2many('migration.model_fields', 'import_model_id', 'Fields'),
        'actions':fields.one2many('migration.model_actions', 'model_id', 'Actions'),
        'domain': fields.text('Domain'),
        'active':fields.boolean('Active'),
        'message': fields.char('Last message', size=128, readonly=True),
		'workflow':fields.boolean('Create workflow', help="Create a workflow for each imported object"),
    }
    '''
    _constraints = [
            (_check_model_fields, '', ['name']),
        ]
    '''

    _defaults = {
        'sequence': _get_sequence,
        'active': lambda *a: True,
		'workflow': lambda *a: False,
    }

migration_import_models()

#imported_records = {}
#warning_text = []
#print_log = False

def create(self, cr, user, vals, context=None):
    if not context:
        context = {}
    self.pool.get('ir.model.access').check(cr, user, self._name, 'create', context=context)

    default = []

    avoid_table = []
    for (t, c) in self._inherits.items():
        if c in vals:
            avoid_table.append(t)
    for f in self._columns.keys():
        if (not f in vals) and (not isinstance(self._columns[f], fields.property)):
            default.append(f)

    for f in self._inherit_fields.keys():
        if (not f in vals) and (self._inherit_fields[f][0] not in avoid_table) and (not isinstance(self._inherit_fields[f][2], fields.property)):
            default.append(f)

    if len(default):
        default_values = self.default_get(cr, user, default, context)
        for dv in default_values:
            if dv in self._columns and self._columns[dv]._type == 'many2many':
                if default_values[dv] and isinstance(default_values[dv][0], (int, long)):
                    default_values[dv] = [(6, 0, default_values[dv])]
        vals.update(default_values)

    tocreate = {}
    for v in self._inherits:
        if self._inherits[v] not in vals:
            tocreate[v] = {}

    (upd0, upd1, upd2) = ('', '', [])
    upd_todo = []

    for v in vals.keys():
        if v in self._inherit_fields:
            (table, col, col_detail) = self._inherit_fields[v]
            tocreate[table][v] = vals[v]
            del vals[v]

    # Try-except added to filter the creation of those records whose filds are readonly.
    # Example : any dashboard which has all the fields readonly.(due to Views(database views))
    try:
        cr.execute("SELECT nextval('"+self._sequence+"')")
    except:
        raise except_orm(_('UserError'),
                    _('You cannot perform this operation.'))

    id_new = cr.fetchone()[0]
    for table in tocreate:
        #id = self.pool.get(table).create(cr, user, tocreate[table])
        id = create(self.pool.get(table), cr, user, tocreate[table])
        upd0 += ','+self._inherits[table]
        upd1 += ',%s'
        upd2.append(id)
    
    #Start : Set bool fields to be False if they are not touched (to make search more powerful) 
    bool_fields = [x for x in self._columns.keys() if self._columns[x]._type=='boolean']
    
    for bool_field in bool_fields:
        if bool_field not in vals:
            vals[bool_field] = False
    #End
    
    for field in vals:
        if field in self._columns:
            if self._columns[field]._classic_write:
                upd0 = upd0 + ',"' + field + '"'
                upd1 = upd1 + ',' + self._columns[field]._symbol_set[0]
                upd2.append(self._columns[field]._symbol_set[1](vals[field]))
            else:
                upd_todo.append(field)
        if field in self._columns \
                and hasattr(self._columns[field], 'selection') \
                and vals[field]:
            if self._columns[field]._type == 'reference':
                val = vals[field].split(',')[0]
            else:
                val = vals[field]
            if isinstance(self._columns[field].selection, (tuple, list)):
                if val not in dict(self._columns[field].selection):
                    raise except_orm(_('ValidateError'),
                    _('The value "%s" for the field "%s" is not in the selection ("%s")') \
                            % (vals[field], field, self._name))
            else:
                if val not in dict(self._columns[field].selection(
                    self, cr, user, context=context)):
                    raise except_orm(_('ValidateError'),
                    _('The value "%s" for the field "%s" is not in the selection ("%s")') \
                            % (vals[field], field, self._name))
    if self._log_access:
        upd0 += ',create_uid,create_date'
        upd1 += ',%s,now()'
        upd2.append(user)
    cr.execute('insert into "'+self._table+'" (id'+upd0+") values ("+str(id_new)+upd1+')', tuple(upd2))
    upd_todo.sort(lambda x, y: self._columns[x].priority-self._columns[y].priority)

    if self._parent_store:
        if self.pool._init:
            self.pool._init_parent[self._name]=True
        else:
            parent = vals.get(self._parent_name, False)
            if parent:
                cr.execute('select parent_right from '+self._table+' where '+self._parent_name+'=%s order by '+(self._parent_order or self._order), (parent,))
                pleft_old = None
                result_p = cr.fetchall()
                for (pleft,) in result_p:
                    if not pleft:
                        break
                    pleft_old = pleft
                if not pleft_old:
                    cr.execute('select parent_left from '+self._table+' where id=%s', (parent,))
                    pleft_old = cr.fetchone()[0]
                pleft = pleft_old
            else:
                cr.execute('select max(parent_right) from '+self._table)
                pleft = cr.fetchone()[0] or 0
            cr.execute('update '+self._table+' set parent_left=parent_left+2 where parent_left>%s', (pleft,))
            cr.execute('update '+self._table+' set parent_right=parent_right+2 where parent_right>%s', (pleft,))
            cr.execute('update '+self._table+' set parent_left=%s,parent_right=%s where id=%s', (pleft+1,pleft+2,id_new))
            
    # default element in context must be removed when call a one2many or many2many
    rel_context = context.copy()
    for c in context.items():
        if c[0].startswith('default_'):
            del rel_context[c[0]]
    
    result = []
    for field in upd_todo:
        result += self._columns[field].set(cr, self, id_new, field, vals[field], user, rel_context) or []
    #self._validate(cr, user, [id_new], context)

    if not context.get('no_store_function', False):
        result += self._store_get_values(cr, user, [id_new], vals.keys(), context)
        result.sort()
        done = []
        for order, object, ids, fields2 in result:
            if not (object, ids, fields2) in done:
                self.pool.get(object)._store_set_values(cr, user, ids, fields2, context)
                done.append((object, ids, fields2))

    return id_new

class migration_model_actions(osv.osv):
    _name = 'migration.model_actions'
    
    _columns = {
        'name':fields.char('Function Name', size=64, required=True),
        'model': fields.many2one('ir.model', 'Model'),
        'args':fields.char('Arguments', size=128),
        'model_id':fields.many2one('migration.import_models', 'Import model', ondelete='cascade'),
        'do_all':fields.boolean('Do for all records'),
        
    }

    _defaults = {
        'do_all': lambda *a: True,
        'args': lambda *a: '[]',
    }

migration_model_actions()

class migration_schedule(osv.osv):
    _name = 'migration.schedule'
    _rec_name = 'date'
    _description = 'Scheduled migration models'

    def __init__(self, pool, cr):
        pool.add(self._name, self)
        self.imported_records = {}
        self.warning_text = []
        self.pool = pool
        osv.osv.__init__(self, pool, cr)

    def _callback(self, cr, uid, model, func, args):
        args = (args or []) and eval(args)
        m=self.pool.get(model)
        if m and hasattr(m, func):
            f = getattr(m, func)
            f(cr, uid, *args)

    def search_old(self, sock, db_name, uid, password):
        def search(model_name, domain):
            return sock.execute(db_name, uid, password, model_name, 'search', domain)
        return search

    def read_old(self, sock, db_name, uid, password):
        def read(model_name, ids, fields):
            return sock.execute(db_name, uid, password, model_name, 'read', ids, fields)
        return read

    def import_model(self, cr, uid, sock, remote_config, remote_uid, model_id, ref_ids=[], exc_field=None):
        #global imported_records
        #global warning_text
        #global print_log
        results = []
        model_name = self.pool.get("migration.import_models").browse(cr, uid, model_id, {}).name.model
        old_model_name = self.pool.get("migration.import_models").browse(cr, uid, model_id, {}).old_name.model or model_name
        domain = self.pool.get("migration.import_models").browse(cr, uid, model_id, {}).domain
        model_obj = self.pool.get(model_name)
        if self.print_log:
            print "Import_model:",model_name
            #print imported_records
            for i in self.imported_records:
                print i+':', len(self.imported_records[i])
        model_field_ids = map(int, self.pool.get("migration.import_models").browse(cr, uid, model_id, {}).field)
        many2one_fields = {}
        one2many_fields = {}
        many2many_fields = {}
        selection_fields = {}
        other_fields = []
        old2new_fields = {}
        im_ids = self.pool.get("migration.import_models").search(cr, uid, [])
        model_names_list = [x.name.model for x in self.pool.get("migration.import_models").browse(cr, uid, im_ids, {})]
        for model_field in self.pool.get("migration.model_fields").browse(cr, uid, model_field_ids, {}):
            if model_field.old_name:
                curr_field = model_field.old_name
            else:
                curr_field = model_field.name

            if model_field.name:
                old2new_fields[model_field.old_name.name or model_field.name.name] = model_field.name.name
            elif model_field.old_name.name:
                old2new_fields[model_field.old_name.name] = False

            if curr_field.ttype=='many2one':
                many2one_fields[curr_field.name] = curr_field.relation
            elif curr_field.ttype=='one2many':
                one2many_fields[curr_field.name] = curr_field.relation
            elif curr_field.ttype=='many2many':
                many2many_fields[curr_field.name] = curr_field.relation
            elif model_field.name.ttype=='selection':
                if isinstance(model_obj._columns[model_field.name.name].selection, (tuple, list)):
                    selection_fields[curr_field.name] = [x[0] for x in model_obj._columns[model_field.name.name].selection]
                else:
                    other_fields.append(curr_field.name)
            else:
                other_fields.append(curr_field.name)

            if model_field.name.relation and model_field.name.relation!='NULL' and model_field.name.relation not in model_names_list:
                msg_text = 'Warning! Object "'+model_name+'" have relation field \''+model_field.name.name+'\' which related to object "'+model_field.name.relation+'", this field was not filled because related object\'s model is not added in Import Model list.\n\n'
                if msg_text not in self.warning_text:
                    self.warning_text.append(msg_text)
            fields_list = many2one_fields.keys()+one2many_fields.keys()+many2many_fields.keys()+selection_fields.keys()+other_fields
        active_field = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], 'ir.model.fields', 'search', [('model','=', old_model_name),('name','=','active')])
        rec_ids = sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], old_model_name, 'search', [])
        if active_field:
            rec_ids += sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], old_model_name, 'search', [('active','!=',True)])
        if ref_ids and type(ref_ids)!=list: ref_ids = [ref_ids]
        #print fields_list
        for model_data in sock.execute(remote_config['db_name'], remote_uid, remote_config['password'], old_model_name, 'read', ref_ids or rec_ids, fields_list):
            #print "Before:",model_data
            old_values = model_data.copy() # save old values
            search_old = self.search_old(sock=sock, db_name=remote_config['db_name'], uid=remote_uid, password=remote_config['password'])
            read_old = self.read_old(sock=sock, db_name=remote_config['db_name'], uid=remote_uid, password=remote_config['password'])
            if domain:
                filter_data = {"fields":model_data,"self":self,"cr":cr,"uid":uid}
                exec domain in filter_data
                if not filter_data.get('is_valid', False):
                    continue
            ######## Remove fields which not exist in new data base
            for k in model_data.keys():
                if k!='id' and k not in fields_list:
                    del model_data[k]
            #######################################################
            #if model_data.get(exc_field, False): del model_data[exc_field]
            for md in model_data:
                if md in many2one_fields and model_data[md]:
                    if isinstance(model_data[md], list):
                        ref = model_data[md][0]
                    else:
                        ref = model_data[md]
                    rel_model_name = many2one_fields[md]
                    ##### Search imported records ID and if current record ID is in imported records list, then use this ID #####
                    imr = self.imported_records.get(rel_model_name, {})
                    if imr.get(ref, False):
                        model_data[md] = imr[ref]
                        continue
                    elif old2new_fields[md]:
                        if not model_obj._columns[old2new_fields[md]].required and ref in imr:
                            model_data[md] = False
                            continue
                    else:
                        if ref in imr:
                            model_data[md] = False
                            continue
                    #elif not model_obj._columns[old2new_fields[md]].required and ref in imr:
                    #elif ref in imr:
                    #    model_data[md] = False
                    #    continue
                    #############################################################################################################
                    rel_model_id = self.pool.get("ir.model").search(cr, uid, [('model','=',rel_model_name)], limit=1)
                    rel_import_model_id = self.pool.get("migration.import_models").search(cr, uid, [('name','=',rel_model_id)], limit=1)
                    if rel_import_model_id:
                        if exc_field:
                            rel_field = md
                        else:
                            rel_field = None
                        res = self.import_model(cr, uid, sock, remote_config, remote_uid, rel_import_model_id[0], ref, rel_field)
                        if res:
                            model_data[md] = res[0]['id']
                        else:
                            model_data[md] = False
                    else:
                        model_data[md]=False
                elif md in one2many_fields:
                    rel_model_name = one2many_fields[md]
                    if not model_data[md] or model_obj._columns[old2new_fields[md]]._fields_id==exc_field or set(self.imported_records.get(rel_model_name,{})).issuperset(set(model_data[md])):
                        model_data[md] = None
                        continue
                    ref_list = model_data[md]
                    refs = []
                    res_data = []
                    rel_model_id = self.pool.get("ir.model").search(cr, uid, [('model','=',rel_model_name)], limit=1)
                    rel_import_model_id = self.pool.get("migration.import_models").search(cr, uid, [('name','=',rel_model_id)], limit=1)
                    if rel_import_model_id and ref_list:
                        rel_field = model_obj._columns[old2new_fields[md]]._fields_id

                        rel_model_ids = self.imported_records.setdefault(rel_model_name, {})
                        for ref in ref_list:
                            if not rel_model_ids.get(ref):
                                rel_model_ids[ref]=False
                        self.imported_records[rel_model_name] = rel_model_ids

                        if len(ref_list)==2 and type(ref_list[1]) in (str, unicode): ref_list=ref_list[0]
                        res = self.import_model(cr, uid, sock, remote_config, remote_uid, rel_import_model_id[0], ref_list, rel_field)
                        #res_data += [(0,0,r) for r in res]
                        res_data = [(6,0,[r['id'] for r in res])]
                        model_data[md] = res_data
                    else:
                        model_data[md]=False
                elif md in many2many_fields:
                    ref_list = model_data[md]
                    rel_model_name = many2many_fields[md]
                    refs = []
                    rec_list = []
                    for ref in ref_list:
                        if self.imported_records.get(rel_model_name, {}).get(ref, False):
                            rec_list.append(self.imported_records[rel_model_name][ref])
                        else:
                            refs.append(ref)
                    res_data = []
                    if rec_list:
                        res_data += [(6,0,rec_list)]
                        #res_data += [(0,0,r) for r in rec_list]
                    else:
                        res_data = []
                    rel_model_id = self.pool.get("ir.model").search(cr, uid, [('model','=',rel_model_name)], limit=1)
                    rel_import_model_id = self.pool.get("migration.import_models").search(cr, uid, [('name','=',rel_model_id)], limit=1)
                    if rel_import_model_id and refs:
                        res_new = self.import_model(cr, uid, sock, remote_config, remote_uid, rel_import_model_id[0], refs)
                        #res_data += [(0,0,r) for r in res_new]
                        res_data += [(6,0,[r['id'] for r in res_new])]
                    model_data[md] = res_data
                else:
                    pass

            localspace = {"fields":model_data,"self":self,"cr":cr,"uid":uid,"old_values":old_values,"search_old":search_old,"read_old":read_old,"mapping":self.imported_records}
            ######## Fill fields with Python constructor ############
            for mf in self.pool.get("migration.model_fields").browse(cr, uid, model_field_ids, {}):
                if mf.used_field_value:
                    try:
                        exec mf.field_value in localspace
                    except Exception, e:
                        try:
                            msg_error = str(e)
                        except:
                            msg_error = _('Unknown')                        
                        msg_text = _('Error! Object "%s" has Python code error in field "%s".\nException arised: %s\n\n') % (model_name, mf.field_name, msg_error)
                        self.warning_text.append(msg_text)
                        raise
                    model_data[mf.old_name.name or mf.name.name] = localspace.get('value')
            #########################################################
            for md in model_data:
                if md in selection_fields:
                    if model_data[md] not in selection_fields[md]:
                        defaults = self.pool.get(model_name)._defaults
                        if md in defaults:
                            model_data[md] = defaults[md]
                        else:
                            model_data[md] = selection_fields[md][0]
            old_id = model_data['id']
            if self.imported_records.get(model_name, {}).get(old_id, False):
                results.append({'id':self.imported_records.get(model_name, {}).get(old_id)})
                continue
            ref_list = self.imported_records.setdefault(model_name, {})
            ref_list[old_id]=False
            self.imported_records[model_name] = ref_list

            del model_data['id']
            #### Replace old field names to new field names
            mdata_final = {}
            for md in model_data:
                if old2new_fields.get(md, False):
                    mdata_final[old2new_fields[md]] = model_data[md]
            ###############################################
            #print "After:",mdata_final
            #res_id = super(pool.get(model_name).__class__, pool.get(model_name)).create(cr, uid, mdata_final)
            res_id = create(self.pool.get(model_name), cr, uid, mdata_final)
            ref_list[old_id]=res_id
            self.imported_records[model_name] = ref_list
            mdata_final['id'] = res_id
            results.append(mdata_final)

            ############# Workflow ############
            if self.pool.get("migration.import_models").browse(cr, uid, model_id, {}).workflow:
                print "Workflow: ", model_name, res_id
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_create(uid, model_name, res_id, cr)
            ###################################
        return results

    def make_warning_message(self):
        warning = ''
        if self.warning_text:
            warning += '<<<<<<<<<<<<<<<< Warning! >>>>>>>>>>>>>>>>\n'
            warning += reduce(lambda x, y: x+y, self.warning_text)
        return warning

    def _import_data(self, cr, uid, self_id, model_ids, context={}):
        #global imported_records
        #global warning_text
        #global print_log
        ############# Get Connection ############
        id = self.pool.get('migration.server.connect_config').search(cr, uid, [], limit=1)
        remote_config = self.pool.get('migration.server.connect_config').read(cr, uid, id)[0]
        sock_common = xmlrpclib.ServerProxy ('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/common', encoding="UTF-8")
        remote_uid = sock_common.login(remote_config['db_name'], remote_config['name'], remote_config['password'])
        sock = xmlrpclib.ServerProxy('http://'+remote_config['host']+':'+str(remote_config['port'])+'/xmlrpc/object', encoding="UTF-8")
        #########################################
        imr_obj = self.pool.get("migration.imported_model_records")
        
        imr_ids = imr_obj.search(cr, uid, [])
        for imr in imr_obj.browse(cr, uid, imr_ids, {}):
            self.imported_records[imr.model_id.model] = eval(imr.records_dict or '{}')
        
        cron_id = self.browse(cr, uid, self_id, {}).cron_id.id
        self.print_log = self.browse(cr, uid, self_id, {}).print_log
        self.write(cr, uid, self_id, {'state':'running'})
        cr.commit()
        for id in model_ids:
            try:
                res = self.import_model(cr, uid, sock, remote_config, remote_uid, id)
            except Exception, e:
                tb_s = '<<<<<<<<<<<<<<<< Error! >>>>>>>>>>>>>>>>\n'
                for t in traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback):
                    tb_s += t
                tb_s += '\n'
                cr.rollback()
                warning = self.make_warning_message()
                #self.imported_records.clear()
                self.warning_text = []
                self.write(cr, uid, self_id, {'log':warning+unicode(tb_s, "UTF-8"),'state':'error'})
                return
        #### Write in DB mapping of imported records ids ####
        for imr in self.imported_records:
            model_id = self.pool.get('ir.model').search(cr, uid, [('model','=',imr)], limit=1)[0]
            imported_model_id = imr_obj.search(cr, uid, [('model_id','=',model_id)], limit=1)
            records_dict = self.imported_records.get(imr, {})
            if imported_model_id:
                imr_obj.write(cr, uid, imported_model_id, {
                    'records_dict':str(records_dict),
                    'num_records': len(records_dict),
                })
            else:
                imr_obj.create(cr, uid, {
                    'records_dict':str(self.imported_records.get(imr, {})),
                    'num_records': len(records_dict),
                    'model_id':model_id,
                })
        #####################################################
        cr.commit()
        ############# Actions #############
        actions_obj = self.pool.get("migration.model_actions")
        actions_ids = map(int, self.browse(cr, uid, self_id, {}).actions_ids)
        for act in actions_obj.browse(cr, uid, actions_ids, {}):
            if act.do_all:
                args = eval(act.args)
                args.insert(0, self.pool.get(act.model.model).search(cr, uid, []))
                act.args=str(args)
            self._callback(cr, uid, act.model.model, act.name, act.args)
        ###################################
        warning = self.make_warning_message()
        res_text = '\n'
        for i in sorted(self.imported_records):
            res_text+=i+': '+str(len(self.imported_records[i]))+'\n'
        self.imported_records.clear()
        self.warning_text = []
        self.write(cr, uid, self_id, {'log':warning+res_text,'state':'done'})
        return

    _columns = {
        'name':fields.char('Name', size=64),
        'date': fields.date('Date', required=True),
        'import_model_ids':fields.many2many('migration.import_models', 'schedule_models_rel', 'schedule_id', 'import_model_id', 'Import Models'),
        'actions_ids': fields.many2many('migration.model_actions', 'schedule_actions_rel', 'schedule_id', 'action_id', 'Actions'),
        'state':fields.selection([('ready','Ready'),('running','Running'),('error','Error'),('done','Done'),('stop','Stopped')], 'State'),
        'log': fields.text('Log'),
        'print_log':fields.boolean('Print Log to Console'),
        'cron_id':fields.many2one('ir.cron', 'Scheduler', readonly=True),
                
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'ready',
    }

    def set_start(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'ready'})
        cron_id = self.browse(cr, uid, ids[0], {}).cron_id.id
        nextcall = (now()+DateTime.RelativeDateTime(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
        self.pool.get('ir.cron').write(cr, uid, cron_id, {'numbercall':1, 'active':True, 'nextcall':nextcall})
        return True

    def set_stop(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'stop'})
        cron_id = self.browse(cr, uid, ids[0], {}).cron_id.id
        self.pool.get('ir.cron').write(cr, uid, cron_id, {'active':False})
        return True

    def test_migration(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'ready'})
        cron_args = self.browse(cr, uid, ids[0], {}).cron_id and self.browse(cr, uid, ids[0], {}).cron_id.args or '[]'
        cron_args = eval(cron_args)
        if len(cron_args) == 2:
            self._import_data(cr, uid, cron_args[0], cron_args[1])
        return True

    def unlink(self, cr, uid, ids, context=None):
        schedules = self.read(cr, uid, ids, ['state', 'cron_id'])
        unlink_ids = []
        for r in schedules:
            if r['state'] == 'done' or r['state'] == 'stop':
                unlink_ids.append(r['id'])
                if r['cron_id']:
                    self.pool.get('ir.cron').unlink(cr, uid, r['cron_id'][0])
            else:
                raise osv.except_osv('Invalid action !', 'Cannot delete scheduled data import(s) which are already running !')
        osv.osv.unlink(self, cr, uid, unlink_ids)
        return True

migration_schedule()

class migration_model_fields(osv.osv):
    _name = "migration.model_fields"

    def _get_field_name(self, cr, uid, ids, field_name, arg=None, context={}):
        res={}
        for p in self.browse(cr, uid, ids, context):
            res[p.id] = p.name.name
        return res

    def change_model(self, cr, uid, ids, field):
        data = {}
        if not field:
            return {'value':{'field_name':False}}
        else:
            model_field = self.pool.get('ir.model.fields').browse(cr, uid, field, {})
            data['field_name'] = model_field.name
        return {'value':data}

    _columns = {
        'name': fields.many2one('ir.model.fields', 'Field', domain="[('model_id', '=', parent.name)]"), #('id', 'not in', map(lambda x:x[2]['name'], parent.field))
        'field_name': fields.function(_get_field_name, method=True, string='Field Name', type='char', size=64),
        'old_name': fields.many2one('migration.old_field', 'Field on the old server', domain="[('model_id', '=', parent.old_name)]"),
        'field_value': fields.text('Value Constructor'),
        'used_field_value': fields.boolean('Use field value constructor'),
        'import_model_id': fields.many2one('migration.import_models', 'Import model', ondelete='cascade'),
    }

migration_model_fields()

class migration_imported_model_records(osv.osv):
    _name = "migration.imported_model_records"
    _rec_name = "model_id"

    _columns = {
        'model_id': fields.many2one('ir.model', 'Model', required=True),
        'num_records': fields.integer('Num. Records'),        
        'records_dict': fields.text('Records'),
    }
    
    _order = "model_id"

migration_imported_model_records()

class migration_configuration(osv.osv):
    _name= "migration.configuration"
    _rec_name = "model_object"
    _columns = {
        'model_object' : fields.char('Model object', size=128),
        'model_object_old_server' : fields.char('Old server model object', size=128),
        'sequence' : fields.char('Sequence', size=128),
        'field_name' : fields.char('Field Name', size=128),
        'field_object_name' : fields.char('Object name', size=128),
        'field_name_old_server' : fields.char('Old server field name', size=128),
        'field_object_name_old_server' : fields.char('Old server object name', size=128),
        }
migration_configuration()
