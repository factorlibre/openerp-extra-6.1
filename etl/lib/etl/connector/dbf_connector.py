# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
"""
 To provide connectivity with dbf file.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.connector import connector
from dbfpy import dbf

class dbf_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with dbf file.
    """
    def __init__(self, uri, bufsize=-1, encoding='utf-8', name='dbf_connector'):
        """
        Required Parameters
        uri      : Path of file.

        Extra Parameters
        bufsize  : Buffer size for reading data.
        encoding : Encoding format.
        name     : Name of connector.
        """
        super(dbf_connector, self).__init__(name)
        self._type = 'connector.dbf_connector'
        self.bufsize = bufsize
        self.encoding = encoding
        self.uri = uri
        self.conn = self.open()

    def open(self):
        """
        Opens dbf file connections.
        """
        return dbf.Dbf(self.uri)

    def close(self):
        """
        Closes dbf file connections.
        """
        return self.conn.close()

    def __getstate__(self):
        res = super(dbf_connector, self).__getstate__()
        res.update({'bufsize':self.bufsize, 'encoding':self.encoding, 'uri':self.uri })#
        return res

    def __setstate__(self, state):
        super(dbf_connector, self).__setstate__(state)
        self.__dict__ = state

    def __copy__(self):
        """
        Overrides copy method.
        """
        res = dbf_connector(self.uri, self.bufsize, self.encoding, self.name)
        return res

def test():
    file_conn = dbf_connector('../../demo/input/dbf_file.dbf.dbf')# /input/DE000446.dbf
    con = file_conn.open()
    file_conn.close()

if __name__ == '__main__':
    test()