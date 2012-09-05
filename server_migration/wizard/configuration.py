# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008-2009 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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

import wizard
import pooler
import xmlrpclib

_form = '''<?xml version="1.0"?>
<form string="Connect to the old server">
	<field name="name" colspan="2"/>
	<field name="password" colspan="2"/>
	<field name="db_name" colspan="2"/>
	<field name="host" colspan="2"/>
	<field name="port" colspan="2"/>
	<field name="metadata" colspan="2"/>
</form>'''

_confirm_form = '''<?xml version="1.0"?>
<form string="Warning!">
	<label string="The metadata of the old server already exist in new data base.\nDo you want rewrite metadata?" colspan="2"/>
</form>'''

_done_form = '''<?xml version="1.0"?>
<form string="Connection successfully">
	<label string="Connection to the old server is successfully" colspan="2"/>
</form>'''

_error_form = '''<?xml version="1.0"?>
<form string="Error">
	<label string="Connection Error!" colspan="2"/>
</form>'''

def _load_data(self, cr, uid, data, ctx={}):
	pool = pooler.get_pool(cr.dbname)
	obj = pool.get('migration.server.connect_config')
	id = obj.search(cr, uid, [])
	if len(id) != 0:
		config = obj.read(cr, uid, id, {})[0]
		if len(config) > 1:
			data['form']['name'] = config['name']
			data['form']['password'] = config['password']
			data['form']['db_name'] = config['db_name']
			data['form']['host'] = config['host']
			data['form']['port'] = config['port']
		form = data['form']
	return data['form']

def _save_data(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	obj = pool.get('migration.server.connect_config')
	###################################################
	model_obj = pool.get('migration.old_model')
	field_obj = pool.get('migration.old_field')
	form = data['form']
	try:
		sock_common = xmlrpclib.ServerProxy ('http://'+form['host']+':'+str(form['port'])+'/xmlrpc/common', encoding="UTF-8")
		remote_uid = sock_common.login(form['db_name'], form['name'], form['password'])
		sock = xmlrpclib.ServerProxy('http://'+form['host']+':'+str(form['port'])+'/xmlrpc/object', encoding="UTF-8")
		model_ids = sock.execute(form['db_name'], remote_uid, form['password'], 'ir.model', 'search', [])
		models = sock.execute(form['db_name'], remote_uid, form['password'], 'ir.model', 'read', model_ids, ['name','model','info','field_id'])
	except Exception, e:
		return 'error'
	if data['form']['metadata']:
	    model_obj_ids = model_obj.search(cr, uid, [])
	    if model_obj_ids:
		    model_obj.unlink(cr, uid, model_obj_ids)
	    for model in models:
		    field_ids = model['field_id']
		    del model['field_id']
		    del model['id']
		    model_obj_id = model_obj.create(cr, uid, model)
		    fields = sock.execute(form['db_name'], remote_uid, form['password'], 'ir.model.fields', 'read', field_ids, ['name','model','relation','relation_field',\
				    'field_description','ttype','selection','required','readonly','size'])
		    for f in fields:
			    f['model_id']=model_obj_id
			    f['ttype'] = f['ttype'].lower()
			    field_obj_id = field_obj.create(cr, uid, f)
    ###################################################
	del data['form']['metadata']
	id = obj.search(cr, uid, [], limit=1)
	if id:
		obj.write(cr, uid, id, data['form'])
	else:
		obj.create(cr, uid, data['form'])
	return 'done'

def _save_data_without_meta(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	obj = pool.get('migration.server.connect_config')
	###################################################
	model_obj = pool.get('migration.old_model')
	field_obj = pool.get('migration.old_field')
	form = data['form']
	try:
		sock_common = xmlrpclib.ServerProxy ('http://'+form['host']+':'+str(form['port'])+'/xmlrpc/common', encoding="UTF-8")
		remote_uid = sock_common.login(form['db_name'], form['name'], form['password'])
		sock = xmlrpclib.ServerProxy('http://'+form['host']+':'+str(form['port'])+'/xmlrpc/object', encoding="UTF-8")
		model_ids = sock.execute(form['db_name'], remote_uid, form['password'], 'ir.model', 'search', [])
		models = sock.execute(form['db_name'], remote_uid, form['password'], 'ir.model', 'read', model_ids, ['name','model','info','field_id'])
	except Exception, e:
		return 'error'
    ###################################################
	del data['form']['metadata']
	id = obj.search(cr, uid, [], limit=1)
	if id:
		obj.write(cr, uid, id, data['form'])
	else:
		obj.create(cr, uid, data['form'])
	return 'done'

def _check_metadata(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	model_obj = pool.get('migration.old_model')
	field_obj = pool.get('migration.old_field')
	form = data['form']
	if data['form']['metadata']:
	    model_obj_ids = model_obj.search(cr, uid, [])
	    field_obj_ids = field_obj.search(cr, uid, [])
	    if model_obj_ids or field_obj_ids:
		    return 'confirm'
	    else:
		    return 'save_yes'
	return 'save_no'

_fields = {
	'name': {'string':'Username', 'type':'char', 'size':15, 'required':True},
	'password': {'string':'Password', 'type':'char', 'size':16, 'required':True, 'password':True},
	'db_name': {'string':'DB name', 'type':'char', 'size':32, 'required':True},
	'host': {'string':'Address', 'type':'char', 'size':16, 'required':True},
	'port': {'string':'Port', 'type':'integer', 'default':8069},
	'metadata': {'string':'Load metadata', 'type':'boolean', 'default':True},
}

#class migr_remote_server_conf_wizard(wizard.interface):
#	states = {
#		'init': {
#			'actions': [_load_data],
#			'result': {'type': 'form', 'arch':_form, 'fields':_fields, 'state':(('end','Close', 'gtk-close'),('save','Connect', 'gtk-ok', True))}
#		},
#		'save': {
#			'actions': [_save_data],
#			'result': {'type':'state', 'state':'end'}
#		}
#	}
#migr_remote_server_conf_wizard('migration.server.connect_config.menu')

class migr_remote_server_conf_wizard(wizard.interface):
	states = {
		'init': {
			'actions': [_load_data],
			'result': {'type': 'form', 'arch':_form, 'fields':_fields, 'state':(('end','Close', 'gtk-close'),('check','Connect', 'gtk-ok', True))}
		},
        'check': {
			'actions': [],
			'result': {'type':'choice','next_state':_check_metadata}
		},
		'confirm': {
			'actions': [],
			'result': {'type': 'form', 'arch':_confirm_form, 'fields':{}, 'state':(('save_no','No', '', True),('save_yes','Yes'))}
		},
		'save_yes': {
			'actions': [],
			'result': {'type':'choice','next_state':_save_data}
		},
		'save_no': {
			'actions': [],
			'result': {'type':'choice','next_state':_save_data_without_meta}
		},
		'error': {
			'actions': [],
			'result': {'type': 'form', 'arch':_error_form, 'fields':{}, 'state':(('end','Close', '', True),)},
		},
		'done': {
			'actions': [],
			'result': {'type': 'form', 'arch':_done_form, 'fields':{}, 'state':(('end','Ok', 'gtk-ok', True),)},
		}
	}
migr_remote_server_conf_wizard('migration.server.connect_config.menu')

