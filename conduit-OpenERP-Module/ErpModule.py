import os.path
import sys;
import xmlrpclib;
from gettext import gettext as _
import logging
log = logging.getLogger("modules.ERP")
import traceback
import conduit
import conduit.dataproviders.DataProvider as DataProvider
import conduit.dataproviders.AutoSync as AutoSync
import conduit.TypeConverter as TypeConverter 
import conduit.Utils as Utils
import conduit.Exceptions as Exceptions
from conduit.datatypes import Rid
import conduit.datatypes.Contact as Contact
import conduit.datatypes.Text as Text
import gtk, gtk.glade,gtk.gdk
import xmlrpclib
import gobject
import vobject

MODULES = {
        "OpenErp"  : { "type": "dataprovider" },
		"OpenERPConverter" : { "type": "converter" },
        }


global selected

class ErpBase(DataProvider.DataProviderBase):

	def __init__(self, *args):
		DataProvider.DataProviderBase.__init__(self)
		self.need_configuration(False)
		self.servername = ""
		self.port = ""
		self.username = ""
		self.password = ""
		self.uids = None
		self.set_configured(False)
		
	def _get_object(self,uid):
		raise NotImplementedError
		

	def _create_object(self, obj):
		log.warn("ghghggjhgjhgjhg")
		raise NotImplementedError
		

	def _update_object(self, uid, obj):
		if self._delete_object(uid):
			uid = self._create_object(obj)
			return uid
		else:
			raise Exceptions.SyncronizeError("Error updating object (uid: %s)" % uid)

	def _delete_object(self, uid):
		raise NotImplementedError

	def refresh(self):
		DataProvider.TwoWay.refresh(self)
		self.uids = []

	def get_all(self):
		DataProvider.TwoWay.get_all(self)
		return self.uids

	def get(self, LUID):
		DataProvider.TwoWay.get(self, LUID)
		return self._get_object(LUID)

	def put(self, obj, overwrite, LUID=None):
		DataProvider.TwoWay.put(self, obj, overwrite, LUID)
		if LUID != None:
			existing = self._get_object(LUID)
			if existing != None:
				if overwrite == True:
					rid = self._update_object(LUID, obj)
					return rid
				else:
					comp = obj.compare(existing)
					# only update if newer
					if comp != conduit.datatypes.COMPARISON_NEWER:
						raise Exceptions.SynchronizeConflictError(comp, existing, obj)
					else:
						# overwrite and return new ID
						rid = self._update_object(LUID, obj)
						return rid

		# if we get here then it is new...
		log.info("Creating new object ")
		rid = self._create_object(obj)
		return rid

	def delete(self, LUID):
		if not self._delete_object(LUID):
			log.warn("Error deleting event (uid: %s)" % LUID)

	def finish(self, aborted, error, conflict):
		DataProvider.TwoWay.finish(self)
		self.uids = None

	def _loadDatabase(self,widget,tree):
		#log.warn("selected %s",self.selected)
		dlg = tree.get_widget("OpenERPConfiguration")
		#oldCursor = dlg.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
		gtk.gdk.flush()
		sourceComboBox = tree.get_widget("combobox")
		store = sourceComboBox.get_model()
		store.clear()
		sock = xmlrpclib.ServerProxy('http://localhost:8069' + '/xmlrpc/db')
		dblist=sock.list()
		log.warn("Database list is %s",dblist)
		index=0
		for db in dblist:
			log.warn("database : %s",db)
			try:
				rowref = store.append((db,index))
				index=index+1
				if db == dblist:
					sourceComboBox.set_active_iter(rowref)
			except Exception,e:
				log.warn("exception: %s",str(e))
		return db
		#sourceComboBox.set_sensitive(True)
		#dlg.window.set_cursor(oldCursor)

	def configure(self, window):
		tree = Utils.dataprovider_glade_get_widget(
				        __file__, 
				        "config.glade",
				        "OpenERPConfiguration")
		#get a whole bunch of widgets
		servername = tree.get_widget("servername")
		port = tree.get_widget("port")
		loadbtn=tree.get_widget("loaddb")
		username = tree.get_widget("username")
		password = tree.get_widget("password")
		sourceComboBox = tree.get_widget("combobox")
		#preload the widgets
		servername.set_text("http://localhost")
		port.set_text("8069")
		username.set_text(self.username)
		password.set_text(self.password)
		store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		sourceComboBox.set_model(store)
		cell = gtk.CellRendererText()
		sourceComboBox.pack_start(cell, True)
		sourceComboBox.add_attribute(cell, 'text', 0)
		sourceComboBox.set_active(0)        
		dlg = tree.get_widget("OpenERPConfiguration")
		dlg.set_transient_for(window)
		signalConnections = { "on_load_database_clicked" : (self._loadDatabase, tree) }
		tree.signal_autoconnect( signalConnections )
		response = Utils.run_dialog (dlg, window)
		
		if response:
			sock1 = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
			user_id =  sock1.login('conduit',username.get_text(),password.get_text())
			self.selected = store.get_value(sourceComboBox.get_active_iter(), 1)

			if user_id:
				log.warn("login successfully %s",user_id)
				"""sock_obj = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
				res = sock_obj.execute('conduit',user_id,'a','res.partner','search',[])
				self.res_address = sock_obj.execute('conduit',user_id,'a','res.partner.address','name_get',res)
				log.warn("object fetched successfully %s",self.res_address)"""
				Msg="Login Successfully"
				msgDlg=gtk.MessageDialog(type=gtk.MESSAGE_INFO,message_format=Msg,buttons=gtk.BUTTONS_OK) 	        
				msgDlg.run()
				msgDlg.destroy()
			else:
				errorMsg="Please Enter Valid Username & password"
				errorDlg=gtk.MessageDialog(type=gtk.MESSAGE_ERROR,message_format=errorMsg,buttons=gtk.BUTTONS_OK) 	        
				errorDlg.run()
				errorDlg.destroy()
				log.warn("Please try again %s",user_id)
				self.set_configured(True)
		dlg.destroy()

	def get_configuration(self):
		log.warn("inside get_config")
		config = dict()
		if username is not None:
			config['username'] = username.get_text()
			config['password'] = password.get_text()
		return config
	
	def set_configuration(self, config):
		log.warn("inside set_configuration")

	def get_UID(self):
		return self.username

class OpenErp(ErpBase,DataProvider.TwoWay):
	DEFAULT_DATABASE = "conduit"

	_name_ = "OpenERP"
	_description_ = "Sync VCARDS with OPENERP"
	_category_ = conduit.dataproviders.CATEGORY_MISC
	_module_type_ = "twoway"
	_in_type_ = "contact"
	_out_type_ = "contact"
	_icon_ = ""
	_configurable_ = True

	def __init__(self):
		ErpBase.__init__(self, OpenErp.DEFAULT_DATABASE)
		self.need_configuration(False)

	def _get_object(self, LUID):
		sock_obj = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
		res = sock_obj.execute('conduit',1,'a','res.partner','search',[])
		res_address = sock_obj.execute('conduit',1,'a','res.partner.address','search',[])
		log.warn("object fetched successfully %s",res_address)
		return res_address

	def _create_object(self,contact):
		abc = str(contact).split()
		a = []
		for i in range(0,len(abc)):
			a.append(abc[i].partition(':')[2])
			
		sock_obj = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
		res = sock_obj.execute('conduit',1,'a','res.partner','search',[])
		for i in abc:
			if i.find('CITY')==0:
				city= i.split(':')[1]
			if i.find('FN')==0:
				FN= i.split(':')[1]
			if i.find('N')==0:
				N= i.split(':')[1]
			if i.find('EMAIL')==0:
				EMAIL= i.split(':')[1]
			if i.find('TEL')==0:
				TEL= i.split(':')[1]
			if i.find('MOBILE')==0:
				MOBILE= i.split(':')[1]
			if i.find('STREET')==0:
				STREET= i.split(':')[1]
			if i.find('STREET2')==0:
				STREET2= i.split(':')[1]
			if i.find('ZIP')==0:
				ZIP= i.split(':')[1]
			if i.find('FAX')==0:
				FAX= i.split(':')[1]
		data_partner = {
					'name':FN,
					}
		ids = sock_obj.execute('conduit',1,'a','res.partner','create',data_partner)
		
		data_map = {
		
					'name':N,
					'partner_id':ids,
					'email':EMAIL,
					'mobile':MOBILE,
					'phone':TEL,
					'city':city,
					'street':STREET,
					'street2':STREET2,
					'zip':ZIP,
					'fax':FAX,
					'country_id':101,
					'state_id':1
					}
		res_write=sock_obj.execute('conduit',1,'a','res.partner.address', 'create', data_map)
		return res_write
		
	def _update_object(self, uid):
		log.warn("inside update object")
	
	def _delete_object(self, uid):
		log.warn("inside delete object")

	def refresh(self):
		ErpBase.refresh(self)
		sock_obj = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
		res = sock_obj.execute('conduit',1,'a','res.partner','search',[])
		res_ids = sock_obj.execute('conduit',1,'a','res.partner.address','search',[])
		res_field = sock_obj.execute('conduit',1,'a', 'res.partner.address' , 'fields_get')
		for ids in res_ids:
			res_address = sock_obj.execute('conduit',1,'a', 'res.partner.address','read',[ids])
		for address_type in res_address:
			log.warn("inside addres refresh")
		return res_address

	def configure(self, window):
		self.sourceURI = ErpBase.configure(self,window)


class OpenERPConverter(TypeConverter.TypeConverter,AutoSync.AutoSync):

    def __init__(self):
		AutoSync.AutoSync.__init__(self)
		self.conversions = {
			"vcard,vcard" : self.transcode,
			"text,vcard" : self.convert_to_vcard,
			"vcard,text" : self.convert_to_OpenERP,
			}


    def transcode(self, test, **kwargs):
		log.debug("TEST CONVERTER: Transcode %s (args: %s)" % (test, kwargs))
		return test

    def convert_to_vcard(self, text, **kwargs):
		log.warn("inside convert_ to_test")
		#only keep the first char
		char = text.get_string()[0]
		t = TestDataType(char)
		return t

    def convert_to_OpenERP(self, test, **kwargs):
    
       #LOG('vcard =',0,vcard)
		convert_dict = {}
		convert_dict['FN'] = 'first_name'
		convert_dict['N'] = 'last_name'
		convert_dict['TEL'] = 'default_telephone_text'
		edit_dict = {}
		vcard_list = vcard.split('\n')
		for vcard_line in vcard_list:
		  if ':' in vcard_line:
		    property, property_value = vcard_line.split(':')
		    property_value_list = property_value.split(';')
		    property_parameters_list = []
		    property_name = ''
		    if ';' in property:
		      property_list = property.split(';')
		      property_name = property_list[0] #the property name is the 1st element
		      if len(property_list) > 1 and property_list[1] != '':
		        property_parameters_list = property_list[1:len(property_list)]
		        tmp = []
		        for property_parameter in property_parameters_list:
		          if '=' in property_parameter:
		            property_parameter_name, property_parameter_value = \
		                property_parameter.split('=')
		          else:
		            property_parameter_name = property_parameter
		            property_parameter_value = None
		          tmp.append({property_parameter_name:property_parameter_value})
		        property_parameters_list = tmp
		        #now property_parameters_list looks like :
		        # [{'ENCODING':'QUOTED-PRINTABLE'}, {'CHARSET':'UTF-8'}]

		        property_value_list = \
		            self.changePropertyEncoding(property_parameters_list,
		                                        property_value_list)

		    else:
		      property_name=property
		    if isinstance(property_name, unicode):
		      property_name = property_name.encode('utf-8')

		    tmp = []
		    for property_value in property_value_list:
		      if isinstance(property_value, unicode):
		        property_value = property_value.encode('utf-8')
		      tmp.append(property_value)
		    property_value_list = tmp
		    if property_name in convert_dict.keys():
		      if property_name == 'N' and len(property_value_list) > 1:
		        edit_dict[convert_dict['N']] = property_value_list[0]
		        edit_dict[convert_dict['FN']] = property_value_list[1]
		      else:
		        edit_dict[convert_dict[property_name]] = property_value_list[0]
		#LOG('edit_dict =',0,edit_dict)
		return edit_dict

