p# -*- encoding: utf-8 -*-
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
import BaseHTTPServer
import DAV
import os

from xml.dom import ext

from dav_auth import tinyerp_auth
from dav_fs import tinyerp_handler

import threading
import pooler
import netsvc
logger = netsvc.Logger()

db_name = ''
host=''
port=8008

class dav_server(threading.Thread):
	def __init__(self, host, port, db_name=False, directory_id=False):
		super(dav_server,self).__init__()
		self.host = host
		self.port = port
		self.db_name = db_name
		self.directory_id = directory_id

	def run(self):
		server = BaseHTTPServer.HTTPServer
		handler = tinyerp_auth
		handler.db_name = db_name
		handler.IFACE_CLASS  = tinyerp_handler( self.host,self.port,  True )
		handler.verbose = True
		try:
			runner = server( (self.host, self.port), handler )
			runner.serve_forever()
		except Exception, e:
			 logger.notifyChannel(e,self.host,self.port)

try:
	ds = dav_server(host, port)
	ds.start()
except Exception , e:
	logger.notifyChannel(e)
