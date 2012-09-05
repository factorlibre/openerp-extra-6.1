# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from document.nodes import node_res_dir, node_res_obj
from paramiko.sftp_handle import SFTPHandle
import StringIO
import base64
import netsvc
import os
import paramiko,os
import pooler
import time

def _to_unicode(s):
    try:
        return s.encode('ascii')
    except UnicodeError:
        try:
            return s.decode('utf-8')
        except UnicodeError:
            try:
                return s.decode('latin')
            except UnicodeError:
                return s

def _to_decode(s):
    try:
        return s.encode('utf-8')
    except UnicodeError:
        try:
            return s.encode('latin')
        except UnicodeError:
            try:
                return s.decode('ascii')
            except UnicodeError:
                return s

class file_wrapper(StringIO.StringIO):
    def __init__(self, sstr='', ressource_id=False, dbname=None, uid=1, name=''):
        StringIO.StringIO.__init__(self, sstr)
        self.ressource_id = ressource_id
        self.name = name
        self.dbname = dbname
        self.uid = uid
    def close(self, *args, **kwargs):
        db,pool = pooler.get_db_and_pool(self.dbname)
        self.buf = ''
        cr = db.cursor()
        cr.commit()
        try:
            val = self.getvalue()
            val2 = {
                'datas': base64.encodestring(val),
                'file_size': len(val),
            }
            pool.get('ir.attachment').write(cr, self.uid, [self.ressource_id], val2)

        finally:
            cr.commit()
            cr.close()
        return StringIO.StringIO.close(self, *args, **kwargs)

class content_wrapper(StringIO.StringIO):
    def __init__(self, dbname, uid, pool, node, name=''):
        StringIO.StringIO.__init__(self, '')
        self.dbname = dbname
        self.uid = uid
        self.node = node
        self.pool = pool
        self.name = name
    def close(self, *args, **kwargs):
        db,pool = pooler.get_db_and_pool(self.dbname)
        cr = db.cursor()
        cr.commit()
        try:
            getattr(self.pool.get('document.directory.content'), 'process_write_'+self.node.content.extension[1:])(cr, self.uid, self.node, self.getvalue())
        finally:
            cr.commit()
            cr.close()
        return StringIO.StringIO.close(self, *args, **kwargs)

class SFTPServer (paramiko.SFTPServerInterface):
    db_name_list=[]
    def __init__(self, server, *largs, **kwargs):
        self.server = server
        self.ROOT = '/'

    def fs2ftp(self, node):
        res = '/'
        if node:
            res = os.path.normpath(node.path)
            res = res.replace("\\", "/")
            while res[:2] == '//':
                res = res[1:]
            res='/' + node.cr.dbname + '/' + res
        res = _to_decode(res)
        return res

    def ftp2fs(self, path, data):
        if not data or (path and (path in ('/','.'))):
            return None
        path = _to_unicode(path)
        path2 = filter(None,path.split('/'))[1:]
        (cr, uid, pool) = data
        res = pool.get('document.directory').get_object(cr, uid, path2[:])
        if not res:
            raise OSError(2, 'Not such file or directory.')
        return res

    def get_cr(self, path):
        path = _to_unicode(path)
        if path and path in ('/','.'):
            return None
        dbname = path.split('/')[1]
        try:
            if not len(self.db_name_list):
                self.db_name_list = self.db_list()
            if dbname not in self.db_name_list:
                return None
            db,pool = pooler.get_db_and_pool(dbname)
        except:
            raise OSError(1, 'Operation not permited.')
        cr = db.cursor()
        uid = self.server.check_security(dbname, self.server.username, self.server.key)
        if not uid:
            raise OSError(2, 'Authentification Required.')
        return cr, uid, pool

    def close_cr(self, data):
        if data:
            data[0].close()
        return True


    def open(self, node, flags, attr):
        try:
            if not node:
                raise OSError(1, 'Operation not permited.')
            cr = pooler.get_db(node.context.dbname).cursor()
            uid = node.context.uid
            if node.type=='file':
                if not self.isfile(node):
                    raise OSError(1, 'Operation not permited.')
                att_obj = node.context._dirobj.pool.get('ir.attachment')
                fobj = att_obj.browse(cr, uid, node.file_id, \
                                  context=node.context.context)
                if fobj.store_method and fobj.store_method== 'fs' :
                    f = StringIO.StringIO(node.get_data(cr, fobj))
                else:
                    f = StringIO.StringIO(base64.decodestring(fobj.datas or ''))
            elif node.type=='content':
                pool = pooler.get_pool(cr.dbname)
                res = getattr(pool.get('document.directory.content'), 'process_read')(cr, uid, node)
                f = StringIO.StringIO(res)
            else:
                raise OSError(1, 'Operation not permited.')
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

        sobj = SFTPHandle(flags)
        sobj.filename = node.path
        sobj.readfile = f
        sobj.writefile = None
        cr.close()
        return sobj

    def create(self, node, objname, flags):
        objname=_to_unicode(objname)
        cr = None
        try:
            uid = node.context.uid
            pool = pooler.get_pool(node.context.dbname)
            cr = pooler.get_db(node.context.dbname).cursor()
            child = node.child(cr, objname)
            f = None
            if child:
                if child.type in ('collection','database'):
                    raise OSError(1, 'Operation not permited.')
                if child.type=='content':
                    f = content_wrapper(cr.dbname, uid, pool, child)
            fobj = pool.get('ir.attachment')
            ext = objname.find('.') >0 and objname.split('.')[1] or False

            # TODO: test if already exist and modify in this case if node.type=file
            ### checked already exits
            object2 = False
            if isinstance(node, node_res_obj):
                object2 = node and pool.get(node.context.context['res_model']).browse(cr, uid, node.context.context['res_id']) or False            
            
            cid = False
            object = node.context._dirobj.browse(cr, uid, node.context.context['dir_id'])

            where=[('name','=',objname)]
            if object and (object.type in ('directory')) or object2:
                where.append(('parent_id','=',object.id))
            else:
                where.append(('parent_id','=',False))

            if object2:
                where +=[('res_id','=',object2.id),('res_model','=',object2._name)]
            cids = fobj.search(cr, uid,where)
            if len(cids):
                cid=cids[0]

            if not cid:
                val = {
                    'name': objname,
                    'datas_fname': objname,
                    'datas': '',
                    'file_size': 0L,
                    'file_type': ext,
                }
                if object and (object.type in ('directory')) or not object2:
                    val['parent_id']= object and object.id or False
                partner = False
                if object2:
                    if 'partner_id' in object2 and object2.partner_id.id:
                        partner = object2.partner_id.id
                    if object2._name == 'res.partner':
                        partner = object2.id
                    val.update( {
                        'res_model': object2._name,
                        'partner_id': partner,
                        'res_id': object2.id
                    })
                cid = fobj.create(cr, uid, val, context={})
            cr.commit()
            cr.close()
            f = file_wrapper('', cid, cr.dbname, uid, )

        except Exception,e:
            log(e)
            raise OSError(1, 'Operation not permited.')
        
        if f :
            fobj = SFTPHandle(flags)
            fobj.filename =  objname
            fobj.readfile = None
            fobj.writefile = f
            return fobj
        return False

    def remove(self, node):
        """ Remove  """
        assert node
        if node.type == 'collection':
            return self.rmdir(node)
        elif node.type == 'file':
            return self.rmfile(node)
        raise OSError(1, 'Operation not permited.')

    def rmfile(self, node):
        """Remove the specified file."""
        try:
            cr = pooler.get_db(node.context.dbname).cursor()
            uid = node.context.uid
            pool = pooler.get_pool(node.context.dbname)
            
            object = pool.get('ir.attachment').browse(cr, uid, node.file_id)
            if not object:
                raise OSError(2, 'Not such file or directory.')
            if object._table_name == 'ir.attachment':
                res = pool.get('ir.attachment').unlink(cr, uid, [object.id])
            else:
                raise OSError(1, 'Operation not permited.')
            cr.commit()
            cr.close()
            return paramiko.SFTP_OK
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        
    def db_list(self):
        #return pooler.pool_dic.keys()
        s = netsvc.ExportService.getService('db')
        result = s.exp_list()
        self.db_name_list = []
        for db_name in result:
            db, cr = None, None
            try:
                db = pooler.get_db_only(db_name)
                cr = db.cursor()
                cr.execute("SELECT 1 FROM pg_class WHERE relkind = 'r' AND relname = 'ir_module_module'")
                if not cr.fetchone():
                    continue

                cr.execute("select id from ir_module_module where name like 'document_sftp' and state='installed' ")
                res = cr.fetchone()
                if res and len(res):
                    self.db_name_list.append(db_name)
                cr.commit()
            except Exception,e:
                log(e)
                if cr:
                    cr.rollback()
            finally:
                if cr is not None:
                    cr.close()
        return self.db_name_list

    def list_folder(self, node):
        """ List the contents of a folder """
        try:
            """List the content of a directory."""
            class false_node:
                write_date = None
                create_date = None
                type = 'database'
                def __init__(self, db):
                    self.path = '/'+db

            if node is None:
                result = []
                for db in self.db_list():
                    uid = self.server.check_security(db, self.server.username, self.server.key)
                    if uid:
                        result.append(false_node(db))
                return result
            cr = pooler.get_db(node.context.dbname).cursor()
            res = node.children(cr)
            cr.close()
            return res
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def rename(self, src, dst_basedir, dst_basename):
        """
            Renaming operation, the effect depends on the src:
            * A file: read, create and remove
            * A directory: change the parent and reassign childs to ressource
        """
        cr = False
        try:
            dst_basename=_to_unicode(dst_basename)
            cr = pooler.get_db(src.context.dbname).cursor()
            uid = src.context.uid
            pool = pooler.get_pool(cr.dbname)
            object2 = False
            obj2 = False
            dst_obj2 = False
            if src.type=='collection':
                obj = src.context._dirobj.browse(cr, uid, src.dir_id)
                if obj._table_name <> 'document.directory':
                    raise OSError(1, 'Operation not permited.')
                result = {
                    'directory': [],
                    'attachment': []
                }
                # Compute all childs to set the new ressource ID
                child_ids = [src]
                while len(child_ids):
                    node = child_ids.pop(0)
                    child_ids += node.children(cr)
                    if node.type =='collection':
                        if isinstance(node, node_res_obj):
                            object2 = node and pool.get(node.context.context['res_model']).browse(cr, uid, node.context.context['res_id']) or False
                        obj1 = node.context._dirobj.browse(cr, uid, node.context.context['dir_id'])
                        
                        result['directory'].append(obj1.id)
                        if (not obj1.ressource_id) and object2:
                            raise OSError(1, 'Operation not permited.')
                    elif node.type =='file':
                        result['attachment'].append(obj1.id)

                if object2 and not obj.ressource_id:
                    raise OSError(1, 'Operation not permited.')
                val = {
                    'name': dst_basename,
                }
                if isinstance(dst_basedir, node_res_obj):
                    dst_obj2 = dst_basedir and pool.get(dst_basedir.context.context['res_model']).browse(cr, uid, dst_basedir.context.context['res_id']) or False
                dst_obj = dst_basedir.context._dirobj.browse(cr, uid, dst_basedir.dir_id)
                
                if (dst_obj and (dst_obj.type in ('directory'))) or not dst_obj2:
                    val['parent_id'] = dst_obj and dst_obj.id or False
                else:
                    val['parent_id'] = False
                res = pool.get('document.directory').write(cr, uid, [obj.id],val)
                if dst_obj2:
                    ressource_type_id = pool.get('ir.model').search(cr,uid,[('model','=', dst_obj2._name)])[0]
                    ressource_id = dst_obj2.id
                    title = dst_obj2.name
                    ressource_model = dst_obj2._name
                    if dst_obj2._name == 'res.partner':
                        partner_id = dst_obj2.id
                    else:
                        obj2=pool.get(dst_obj2._name)
                        partner_id= obj2.fields_get(cr,uid,['partner_id']) and dst_obj2.partner_id.id or False
                else:
                    ressource_type_id = False
                    ressource_id=False
                    ressource_model = False
                    partner_id = False
                    title = False

                pool.get('document.directory').write(cr, uid, result['directory'], {
                    'ressource_id': ressource_id,
                    'ressource_type_id': ressource_type_id
                })
                val = {
                    'res_id': ressource_id,
                    'res_model': ressource_model,
                    'title': title,
                    'partner_id': partner_id
                }
                pool.get('ir.attachment').write(cr, uid, result['attachment'], val)
                if (not val['res_id']) and result['attachment']:
                    cr.execute('update ir_attachment set res_id=NULL where id in ('+','.join(map(str,result['attachment']))+')')

                cr.commit()
            elif src.type=='file':
                val = {
                    'partner_id':False,
                    #'res_id': False,
                    'res_model': False,
                    'name': dst_basename,
                    'datas_fname': dst_basename,
                    'title': dst_basename,
                }
                obj = pool.get('ir.attachment').browse(cr, uid, src.file_id)                
                dst_obj2 = False                     
                if isinstance(dst_basedir, node_res_obj):
                    dst_obj2 = dst_basedir and pool.get(dst_basedir.context.context['res_model']).browse(cr, uid, dst_basedir.context.context['res_id']) or False            
                dst_obj = dst_basedir.context._dirobj.browse(cr, uid, dst_basedir.dir_id)


                if (dst_obj and (dst_obj.type in ('directory','ressource'))) or not dst_obj2:
                    val['parent_id'] = dst_obj and dst_obj.id or False
                else:
                    val['parent_id'] = False

                if dst_obj2:
                    val['res_model'] = dst_obj._name
                    val['res_id'] = dst_obj.id
                    val['title'] = dst_obj.name
                    if dst_obj._name=='res.partner':
                        val['partner_id']=dst_obj.id
                    else:
                        obj2=pool.get(dst_obj._name)
                        val['partner_id']= obj2.fields_get(cr,uid,['partner_id']) and dst_obj.partner_id.id or False
                elif obj.res_id:
                    # I had to do that because writing False to an integer writes 0 instead of NULL
                    # change if one day we decide to improve osv/fields.py
                    cr.execute('update ir_attachment set res_id=NULL where id=%s', (obj.id,))

                pool.get('ir.attachment').write(cr, uid, [obj.id], val)
                cr.commit()
            elif src.type=='content':
                src_file=self.open(src,'r')
                dst_file=self.create(dst_basedir,dst_basename,'w')
                dst_file.write(src_file.getvalue())
                dst_file.close()
                src_file.close()
                cr.commit()
                cr.close()
            else:
                raise OSError(1, 'Operation not permited.')
            return paramiko.SFTP_OK
        except Exception,err:
            log(err)
            return paramiko.SFTPServer.convert_errno(e.errno)

    def mkdir(self, node, basename, attr):
        try:
            """Create the specified directory."""
            if not node:
                raise OSError(1, 'Operation not permited.')
            uid = node.context.uid
            pool = pooler.get_pool(node.context.dbname)
            cr = pooler.get_db(node.context.dbname).cursor()
            basename=_to_unicode(basename)
            object2 = False
            if isinstance(node, node_res_obj):
                object2 = node and pool.get(node.context.context['res_model']).browse(cr, uid, node.context.context['res_id']) or False
            obj = node.context._dirobj.browse(cr, uid, node.context.context['dir_id'])
            if obj and (obj.type=='ressource') and not node.object2:
                raise OSError(1, 'Operation not permited.')
            val = {
                'name': basename,
                'ressource_parent_type_id': object and obj.ressource_type_id.id or False,
                'ressource_id': object2 and object2.id or False
            }
            if (obj and (obj.type in ('directory'))) or not object2:
                val['parent_id'] =  obj and obj.id or False
            # Check if it alreayd exists !
            pool.get('document.directory').create(cr, uid, val)
            cr.commit()
            cr.close()
            return paramiko.SFTP_OK
        except Exception,err:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def rmdir(self, node):
        try:
            cr = pooler.get_db(node.context.dbname).cursor()
            uid = node.context.uid
            pool = pooler.get_pool(node.context.dbname)
            
            if isinstance(node, node_res_obj):
                object2 = node and pool.get(node.context.context['res_model']).browse(cr, uid, node.context.context['res_id']) or False
            obj = node.context._dirobj.browse(cr, uid, node.context.context['dir_id'])
            
            if obj._table_name=='document.directory':
                if node.children(cr):
                    raise OSError(39, 'Directory not empty.')
                res = pool.get('document.directory').unlink(cr, uid, [obj.id])
            else:
                raise OSError(39, 'Directory not empty.')
            
            return paramiko.SFTP_OK
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        finally:
            cr.commit()
            cr.close()

    def _realpath(self, path):
        """ Enforce the chroot jail """
        path = self.ROOT + self.canonicalize(path)
        return path

    def isfile(self, node):
        if node and (node.type not in ('collection','database')):
            return True
        return False


    def islink(self, node):
        """Return True if path is a symbolic link."""
        return False


    def isdir(self, node):
        """Return True if path is a directory."""
        if not node:
            return False
        if node and (node.type in ('collection','database')):
            return True
        return False

    def getsize(self, node):
        """Return the size of the specified file in bytes."""
        result = 0L
        if node and node.type=='file':
            result = node.content_length or 0L
        return result

    def getmtime(self, node):
        """Return the last modified time as a number of seconds since
        the epoch."""
        if node and (node.write_date or node.create_date):
            dt = (node.write_date or node.create_date)[:19]
            result = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        else:
            result = time.mktime(time.localtime())
        return result


    """ Represents a handle to an open file """
    def stat(self, node):
        try:
            r = list(os.stat('/'))
            if self.isfile(node):
                r[0] = 33188
            if self.isdir(node):
                r[0] = 16877
            r[6] = self.getsize(node)
            r[7] = self.getmtime(node)
            r[8] = self.getmtime(node)
            r[9] = self.getmtime(node)
            if node and node.path:
                if isinstance(node.path, list):
                    node.path = '/'.join(node.path)
            path =  node and (node.path and node.path.split('/')[-1]) or '.'
            path =  _to_decode(path)
            return paramiko.SFTPAttributes.from_stat(os.stat_result(r), path)
        except OSError, e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    lstat=stat

    def chattr(self, path, attr):
        return paramiko.SFTP_OK

    def symlink(self, target_path, path):
        return paramiko.SFTP_OK

    def readlink(self, path):
        return paramiko.SFTP_NO_SUCH_FILE

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
