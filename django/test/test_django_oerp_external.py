# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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

""" 
Design Mapping name zoook.product.category and execute this script. 
Remember change username, pwd, dbname and port.
It's only a test. This file is not use to production.
"""
import xmlrpclib

username = 'admin' #the user
pwd = 'admin'      #the password of the user
dbname = 'oerp6_zoook'    #the database

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://localhost:8051/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://localhost:8051/xmlrpc/object')

context = ()
code = 'zoook.product.category'
ids = [1,2]
values = sock.execute(dbname, uid, pwd, 'base.external.mapping', 'get_oerp_to_external', code, ids)

for value in values:
    for val, key  in value.iteritems():
        print "field: %s -|- value: %s" % (val, key)
