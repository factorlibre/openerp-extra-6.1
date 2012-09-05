# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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
from osv.osv import osv_pool, object_proxy
from tools.translate import _

import pooler
import time

class res_partner_company_log(osv.osv):
    _name = 'res.partner.company.log'
    _rec_name = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, ondelete='cascade', readonly=True),
        'model_id': fields.many2one('ir.model', 'OpenERP Model', required=True, ondelete='cascade', readonly=True),
        'first_date': fields.datetime('First Date', readonly=True),
        'first_user_id': fields.many2one('res.users', 'User', readonly=True),
        'last_date': fields.datetime('Last Date', readonly=True),
        'last_user_id': fields.many2one('res.users', 'User', readonly=True),
    }

res_partner_company_log()

class res_partner_company_log_rule(osv.osv):
    _name = 'res.partner.company.log.rule'
    _rec_name = 'model_id'

    _columns = {
        'object_id': fields.many2one('ir.model', 'OpenERP Model', required=True),
        'partner_field_id': fields.many2one('ir.model.fields', 'Partner Field', domain="[('model_id', '=', object_id),('ttype','!=','binary')]", required=True),
        "log_write": fields.boolean("Log Writes", help="Select this if you want to keep track of modification on any record of the object of this rule"),
        "log_unlink": fields.boolean("Log Deletes", help="Select this if you want to keep track of deletion on any record of the object of this rule"),
        "log_create": fields.boolean("Log Creates",help="Select this if you want to keep track of creation on any record of the object of this rule"),
        "state": fields.selection((("draft", "Draft"),('running', 'Running')), "State", required=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'log_create': lambda *a: 1,
        'log_unlink': lambda *a: 1,
        'log_write': lambda *a: 1,
    }

res_partner_company_log_rule()

class partner_company_log_objects_proxy(object_proxy):
    """ Uses Object proxy for create/update Partner Company Log of Rules"""

    def execute(self, db, uid, model, method, *args, **kw):
        """
        Overrides Object Proxy execute method
        @param db: the current database
        @param uid: the current user's ID for security checks,
        @param object: Object who's values are being changed
        @param method: get any method and create log

        @return: Returns result as per method of Object proxy
        """
        pool = pooler.get_pool(db)
        model_pool = pool.get('ir.model')
        rule_pool = pool.get('res.partner.company.log.rule')
        cr = pooler.get_db(db).cursor()
        cr.autocommit(True)
        fct_src = super(partner_company_log_objects_proxy, self).execute

        def my_fct(db, uid, model, method, *args):
            rule = False
            model_ids = model_pool.search(cr, uid, [('model', '=', model)])
            model_id = model_ids and model_ids[0] or False

            for model_name in pool.obj_list():
                if model_name == 'res.partner.company.log.rule':
                    rule = True
            if not rule:
                return fct_src(db, uid, model, method, *args)
            if not model_id:
                return fct_src(db, uid, model, method, *args)

            rule_ids = rule_pool.search(cr, uid, [('object_id', '=', model_id), ('state', '=', 'running')])
            if not rule_ids:
                return fct_src(db, uid, model, method, *args)

            for thisrule in rule_pool.browse(cr, uid, rule_ids):
                methods = []
                if thisrule.log_create:
                    methods.append('create')
                if thisrule.log_write:
                    methods.append('write')
                if thisrule.log_unlink:
                    methods.append('unlink')

                if method in methods:
                    if type(args[0]).__name__ == 'list':
                        ids = args[0]
                    else:
                        ids = [1]

                    for id in ids:
                        user = pool.get('res.users').browse(cr, uid, uid)
                        partner_field_name = pool.get('ir.model.fields').browse(cr, uid, thisrule.partner_field_id.id)
                        
                        if partner_field_name.name in args[0]:
                            partner_id = args[0][partner_field_name.name]
                        else:
                            model_obj = pool.get(model).browse(cr, uid, id)
                            partner = getattr(model_obj, partner_field_name.name)
                            partner_id = partner.id

                        res_partner_company_log_ids = pool.get('res.partner.company.log').search(cr, uid, [('company_id','=',user.company_id.id), ('partner_id','=',partner_id), ('model_id','=',model_id)])

                        if len(res_partner_company_log_ids) > 0:
                            values = {'last_date': time.strftime("%Y-%m-%d %H:%M:%S"), 'last_user_id': uid}
                            pool.get('res.partner.company.log').write(cr, uid, res_partner_company_log_ids, values)
                        else:
                            values = {
                                'partner_id': partner_id,
                                'company_id': user.company_id.id,
                                'model_id': model_id,
                                'first_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                'first_user_id': uid,
                            }
                            pool.get('res.partner.company.log').create(cr, uid, values)
                    return fct_src(db, uid, model, method, *args)

                return fct_src(db, uid, model, method, *args)
        try:
            res = my_fct(db, uid, model, method, *args)
            return res
        finally:
            cr.close()
            
partner_company_log_objects_proxy()
