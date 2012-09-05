import xmlrpclib
import sys
import socket
import os
import pythoncom
import time
from manager import ustr

waittime = 10
wait_count = 0
wait_limit = 12

def execute(connector, method, *args):
    global wait_count
    res = False
    try:
        res = getattr(connector,method)(*args)
    except socket.error,e:
        if e.args[0] == 111:
            if wait_count > wait_limit:
                clean()
                sys.exit(1)
            wait_count += 1
            time.sleep(waittime)
            res = execute(connector, method, *args)
        else:
            return res
    wait_count = 0
    return res

class XMLRpcConn(object):
    __name__ = 'XMLRpcConn'
    _com_interfaces_ = ['_IDTExtensibility2']
    _public_methods_ = ['GetDBList', 'login', 'GetAllObjects', 'GetObjList', 'InsertObj', 'DeleteObject', \
                        'ArchiveToOpenERP', 'IsCRMInstalled', 'GetCSList', 'GetPartners', 'GetObjectItems', \
                        'CreateCase', 'MakeAttachment', 'CreateContact', 'CreatePartner', 'getitem', 'setitem']
    _reg_clsctx_ = pythoncom.CLSCTX_INPROC_SERVER
    _reg_clsid_ = "{C6399AFD-763A-400F-8191-7F9D0503CAE2}"
    _reg_progid_ = "Python.OpenERP.XMLRpcConn"
    _reg_policy_spec_ = "win32com.server.policy.EventHandlerPolicy"
    def __init__(self,server='localhost',port=8069,uri='http://localhost:8069'):
        self._server=server
        self._port=port
        self._uri=uri
        self._obj_list=[]
        self._dbname=''
        self._uname='admin'
        self._pwd='a'
        self._login=False
        self._running=False
        self._uid=False
        self._iscrm=True
        self.partner_id_list=None
    def getitem(self, attrib):
        v=self.__getattribute__(attrib)
        return str(v)
    def setitem(self, attrib, value):
        return self.__setattr__(attrib, value)
    def GetDBList(self):
        conn = xmlrpclib.ServerProxy(self._uri + '/xmlrpc/db')
        try:
            db_list = execute(conn, 'list')
            if db_list == False:
                self._running=False
                return []
            else:
                self._running=True
        except:
            db_list=-1
            self._running=True
        return db_list

    def login(self,dbname, user, pwd):
        self._dbname = dbname
        self._uname = user
        self._pwd = pwd
        conn = xmlrpclib.ServerProxy(self._uri + '/xmlrpc/common')
        uid = execute(conn,'login',dbname, ustr(user), ustr(pwd))
        return uid

    def GetAllObjects(self):
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.model','search',[])
        objects = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.model','read',ids,['model'])
        obj_list = [item['model'] for item in objects]
        return obj_list

    def GetObjList(self):
        self._obj_list=list(self._obj_list)
        self._obj_list.sort(reverse=True)
        return self._obj_list

    def InsertObj(self, obj_title,obj_name,image_path):
        self._obj_list=list(self._obj_list)
        self._obj_list.append((obj_title,obj_name,ustr(image_path).encode('iso-8859-1')))
        self._obj_list.sort(reverse=True)

    def DeleteObject(self,sel_text):
        self._obj_list=list(self._obj_list)
        for obj in self._obj_list:
            if obj[0] == sel_text:
                self._obj_list.remove(obj)
                break

    def ArchiveToOpenERP(self, recs, mail):
        import win32ui, win32con
        conn = xmlrpclib.ServerProxy(self._uri + '/xmlrpc/object')
        import eml
        eml_path=eml.generateEML(mail)
        att_name = ustr(eml_path.split('\\')[-1])
        cnt=1
        for rec in recs: #[('res.partner', 3, 'Agrolait')]
            cnt+=1
            obj = rec[0]
            obj_id = rec[1]
            ids=execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.attachment','search',[('res_id','=',obj_id),('name','=',att_name)])
            if ids:
                name=execute(conn,'execute',self._dbname,int(self._uid),self._pwd,obj,'read',obj_id,['name'])['name']
                msg="This mail is already attached to object with name '%s'"%name
                win32ui.MessageBox(msg,"Make Attachment",win32con.MB_ICONINFORMATION)
                continue
            sub = ustr(mail.Subject)
            if len(sub) > 60:
                l = 60 - len(sub)
                sub = sub[0:l]
            res={}
            res['res_model'] = obj
            content = "".join(open(eml_path,"r").readlines()).encode('base64')
            res['name'] = att_name
            res['datas_fname'] = sub+".eml"
            res['datas'] = content
            res['res_id'] = obj_id
            execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.attachment','create',res)

    def IsCRMInstalled(self):
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        id = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.model','search',[('model','=','crm.case')])
        return id

    def GetCSList(self):
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        ids = execute(conn,'execute',self._dbname,int(int(self._uid)),self._pwd,'crm.case.section','search',[])
        objects = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'crm.case.section','read',ids,['name'])
        obj_list = [ustr(item['name']).encode('iso-8859-1') for item in objects]
        return obj_list

    def GetPartners(self):
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        ids=[]
        ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner','search',[],0,100,'create_date')
        obj_list=[]
        for id in ids:
            object = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner','read',[id],['id','name'])[0]
            obj_list.append((object['id'], ustr(object['name']).encode('iso-8859-1')))
        return obj_list

    def GetObjectItems(self, search_list=[], search_text=''):
        res = []
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        for obj in search_list:
            if obj == "res.partner.address":
                ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,obj,'search',['|',('name','ilike',ustr(search_text)),('email','ilike',ustr(search_text))])
                recs = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,obj,'read',ids,['id','name','street','city'])
                for rec in recs:
                    name = ustr(rec['name']).encode('iso-8859-1')
                    if rec['street']:
                        name += ', ' + ustr(rec['street']).encode('iso-8859-1')
                    if rec['city']:
                        name += ', ' + ustr(rec['city']).encode('iso-8859-1')
                    res.append((obj,rec['id'],name))
            else:
                ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,obj,'search',[('name','ilike',ustr(search_text))])
                recs = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,obj,'read',ids,['id','name'])
                for rec in recs:
                    name = ustr(rec['name']).encode('iso-8859-1')
                    res.append((obj,rec['id'],name))
        return res

    def CreateCase(self, section, mail, partner_ids, with_attachments=True):
        res={}
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        res['name'] = ustr(mail.Subject)
        res['note'] = ustr(mail.Body)
        ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'crm.case.section','search',[('name','=',ustr(section))])
        res['section_id'] = ids[0]
        if partner_ids:
            for partner_id in partner_ids:
                res['partner_id'] = partner_id
                partner_addr = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner','address_get',[partner_id])
                res['partner_address_id'] = partner_addr['default']
                id=execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'crm.case','create',res)
                recs=[('crm.case',id,'')]
                if with_attachments:
                    self.MakeAttachment(recs, mail)
        else:
            id=execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'crm.case','create',res)
            recs=[('crm.case',id,'')]
            if with_attachments:
                self.MakeAttachment(recs, mail)

    def MakeAttachment(self, recs, mail):
        attachments = mail.Attachments
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        att_folder_path = os.path.abspath(os.path.dirname(__file__)+"\\dialogs\\resources\\attachments\\")
        if not os.path.exists(att_folder_path):
            os.makedirs(att_folder_path)
        for rec in recs: #[('res.partner', 3, 'Agrolait')]
            obj = rec[0]
            obj_id = rec[1]
            res={}
            res['res_model'] = obj
            for i in xrange(1, attachments.Count+1):
                fn = ustr(attachments[i].FileName).encode('iso-8859-1')
                if len(fn) > 64:
                    l = 64 - len(fn)
                    f = fn.split('.')
                    fn = f[0][0:l] + '.' + f[-1]
                att_path = os.path.join(att_folder_path,fn)
                attachments[i].SaveAsFile(att_path)
                f=open(att_path,"rb")
                content = "".join(f.readlines()).encode('base64')
                f.close()
                res['name'] = ustr(attachments[i].DisplayName)
                res['datas_fname'] = ustr(fn)
                res['datas'] = content
                res['res_id'] = obj_id
                execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'ir.attachment','create',res)

    def CreateContact(self, sel=None, res=None):
        res=eval(str(res))
        self.partner_id_list=eval(self.partner_id_list)
        res['partner_id'] = self.partner_id_list[sel]
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        id = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner.address','create',res)
        return id

    def CreatePartner(self, res):
        res=eval(str(res))
        conn = xmlrpclib.ServerProxy(self._uri+ '/xmlrpc/object')
        ids = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner','search',[('name','=',res['name'])])
        if ids:
            return False
        id = execute(conn,'execute',self._dbname,int(self._uid),self._pwd,'res.partner','create',res)
        return id
