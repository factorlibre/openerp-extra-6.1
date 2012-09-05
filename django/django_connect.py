# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#                       Jesus Martín <jmartin@zikzakmedia.com>
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
from tools.misc import debug
from tools.translate import _

import paramiko
import os

class django_connect(osv.osv):
    _name = 'django.connect'
    _description = "Django Connect"

    def ssh_command(self, cr, uid, id, values, context={}):
        result = False

        basepath = values['basepath']
        if not basepath [-1] == '/':
            basepath += "/"

        if context['command']:
            client = paramiko.SSHClient()
            if values['key']:
                key = values['ssh_key']
                if not os.path.exists(key):
                    raise osv.except_osv(_('Error!'), _('Key SSH %s not avaible. See documentation') % key)
                client.load_system_host_keys(filename=key)
            else:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(str(values['ip']), port=int(values['port']), username=str(values['username']), password=str(values['password']))
            stdin, stdout, stderr = client.exec_command(basepath+context['command'])
            
            for line in stderr:
#                print "Error -> "+line
                result = False
                
            for line in stdout:
#                print "Exit -> "+line
                result = line.strip('\n')

            client.close()
        else:
            result = False

        return result
django_connect()
