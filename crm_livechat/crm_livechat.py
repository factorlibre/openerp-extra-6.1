# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
from osv import fields,osv
from osv import orm
import pooler
import time

def getBoodyPresence(server,port,ssl,uid,password):
    jid=xmpp.protocol.JID(jid)
    cl=xmpp.Client(jid.getDomain(),debug=[])
    cl.connect(('jabber.tinyerp.com',5223))
    

class crm_livechat_jabber(osv.osv):
    _name="crm_livechat.jabber"
    _description= "Livechat Account"
    _columns={
        'name': fields.char("Jabber Account", size=128, required=True),
        'server': fields.char('Server', size=40, required=True),
        'login': fields.char('Account Login', size=32, required=True),
        'password': fields.char('Account Password', size=16, required=True),
        'ssl':fields.selection([('0','No SSL'),('1','SSL with port remapped'),('2','SSL with 5223 or 443 port')], 'SSL Info'),
        'port':fields.char('Port Number',size=05)
    }
    _defaults = {
        'port': lambda *args: '5223',
        'ssl': lambda *args: '2'
    }
crm_livechat_jabber()

#
# When a visitor wants to talk, he has to call start_session
# To know is there is a user available, you can call get_user
# Then close_session when it's finnished
#

class crm_livechat_livechat(osv.osv):
    _name="crm_livechat.livechat"
    _description= "LiveChat Account"
    _columns={
        'name': fields.char("Livechat Account", size=128, required=True),
        'state': fields.selection([('active','Active'),('notactive','Not Active')], "State"),
        'max_per_user': fields.integer('Maximum Customer per User'),
        'session_delay': fields.integer('Minutes to Close a session', help="Put here to number of minutes after which a session is considered as closed"),
        'user_ids': fields.one2many('crm_livechat.livechat.user', 'livechat_id', 'Users Accounts'),
    }
    _defaults = {
        'max_per_user': lambda *args: 5,
        'state': lambda *args: 'notactive'
    }
    def __init__(self, *args, **argv):
        self.session_count = 0
        self.sessions = {}
        return super(crm_livechat_livechat, self).__init__(*args, **argv)

    #
    # return { jabber_id, {jabber_connection_data} }
    # This is used by the web application to get information about jabber accounts
    # The web application put this in his session to now download it at each time
    #


    def get_configuration(self, cr, uid, ids, context={}):
        result = {}
        main_res={}
        for lc in self.browse(cr, uid, [int(ids)], context):
            for u in lc.user_ids:
                result[str(u.id)] = {
                            'name': u.name,
                            'server': u.jabber_id.server,
                            'login':  u.jabber_id.login,
                            'password':  u.jabber_id.password,
                            'port':u.jabber_id.port,
                            'ssl':u.jabber_id.ssl,
                            'state': u.state
                }
                main_res['user']=result
        return main_res

    def get_user(self, cr, uid, id, context={}):
        activeusr=[]
        minu = (9999999,False)
        tmpres={}
        livechat = self.browse(cr, uid, id, context)

        for user in livechat[0].user_ids:
            
            tmpres = {
                            'name': user.name,
                            'server': user.jabber_id.server,
                            'login':  user.jabber_id.login,
                            'password':  user.jabber_id.password,
                            'port':user.jabber_id.port,
                            'ssl':user.jabber_id.ssl,
                            'state': user.state,
                            'id' : user.id
            }
        
            if  user.state=='active':
                activeusr.append(tmpres)
                c = 0
                
                for s in self.sessions:
                    if s==user.user_id.id:
                        c+=1
                        
                if c<minu[0]:
                    if c<livechat[0].max_per_user:
                        minu = (c, user.id)
            
            else:
                continue
        lst= []
        for x in activeusr:
            lst.append(x['id'])
        return lst

    """
        IN:
            livechat_id
            user_id : False (auto-detect) or force a particular user
            partner_ip: IP Address of the partner
            lang: language of the partner (False for unknown)
        OUT:
            False if no available users or partners
            (session_id, user_jabber_id, partner_jabber_id) if available
    """
    def start_session(self, cr, uid, livechat_id, user_id=False, partner_ids=False, partner_ip='Unknown', lang=False, context={}):
        partner_ids=int(partner_ids)
        if not user_id:
            user_id = self.get_user(cr, uid, livechat_id, context)
        if not user_id:
            return False
        self.pool.get('crm_livechat.livechat.partner').write(cr, uid, [partner_ids], {
            'available': partner_ip,
            'available_date': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self.session_count+=1
        self.sessions[self.session_count] = (user_id, partner_ids, livechat_id)
        return self.session_count
    """
        IN:
            livechat_id
            session_id : The ID of a session
        OUT:
            True
    """
    def stop_session(self, cr, uid, id, session_id, log=True, chat_data='', context={}):
        
        self.pool.get('crm_livechat.livechat.partner').write(cr, uid, self.sessions, {
            'available': False,
        })
        if session_id in self.sessions:
            if log:
                self.pool.get('crm_livechat.log').create(cr, uid, {
                    'note': chat_data,
                    'user_id': self.sessions[session_id][0][1],
                    'livechat_id':self.sessions[session_id][2][0],
                })
            del self.sessions[session_id]
        return True
    
crm_livechat_livechat()

#
# The available jabber accounts for the visitors of the website
#
class crm_livechat_livechat_partner(osv.osv):
    _name="crm_livechat.livechat.partner"
    _description= "LiveChat Visitors"
    _columns={
        'name': fields.char("Account Name", size=128, required=True),
        'jabber_id': fields.many2one('crm_livechat.jabber', "Jabber Account", required=True),
#       'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True),
        'available': fields.char('Available IP', size=64, help="If empty, the acount is available/not used"),
        'available_date': fields.datetime('Available Date'),
        'state': fields.selection([('active','Active'),('notactive','Not Active')], "State", required=True),
    }
    _defaults = {
        'state': lambda *args: 'active'
    }

    def get_live_parnter(self,cr,uid,context={}):
        res={}
        id=self.search(cr,uid,[('state','=','active'),('available','=',False)],context)
        for p in self.browse(cr, uid, id, context):
            if p.available==False:
                        res['id']=p.id
                        res['name']=p.jabber_id.name
                        res['jid']=p.jabber_id.login
                        res['pwd']=p.jabber_id.password
                        res['server']=p.jabber_id.server
                        res['port']=p.jabber_id.port
                        res['ssl']=p.jabber_id.ssl
                        return res
        return res

crm_livechat_livechat_partner()

class crm_livechat_livechat_user(osv.osv):
    _name="crm_livechat.livechat.user"
    _description= "LiveChat Users"
    _columns={
        'name': fields.char("User Name", size=128, required=True),
        'user_id': fields.many2one('res.users', "User", required=True),
        'jabber_id': fields.many2one('crm_livechat.jabber', "Jabber Account", required=True),
        'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True),
        'languages': fields.char('Language Regex', size=128),
        'state': fields.selection([('active','Active'),('notactive','Not Active')], "State", required=True),
    }
    _defaults = {
        'state': lambda *args: 'notactive'
    }
crm_livechat_livechat_user()

class crm_livechat_livechat_log(osv.osv):
    _name="crm_livechat.log"
    _description= "LiveChat Log"
    _order = 'id desc'
    _columns={
        'name': fields.datetime("Date and Time", required=True),
        'user_id': fields.many2one('crm_livechat.livechat.user', "User"),
        'livechat_id': fields.many2one("crm_livechat.livechat", "Livechat", required=True, ondelete='cascade'),
        'note': fields.text('History')
    }
    _defaults = {
        'name': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S')
    }
crm_livechat_livechat_log()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

