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
 To read data from dbf file.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.component import component

class dbf_in(component):
    """
    This is an ETL Component that is used to read data from csv file. Its type is data component.
    Its computing peformance is streamline.
    It has two flows
        Input Flows    : 0.
        * .*           : Nothing.
        Output Flows   : 0-x.
        * .*           : Returns the main flow with data from dbf file.
    """

    def __init__(self, dbfconnector, name='component.input.dbf_in', transformer=None,):
        """
        Required  Parameters
        dbfconnector   : dbf file connector.

        Extra Parameters
        name            : Name of Component.
        transformer     : Transformer object to transform string data into  particular object.
        """
        super(dbf_in, self).__init__(name=name, connector=dbfconnector, transformer=transformer)
        self.dbf_connector = dbfconnector
        self._type = 'component.input.dbf_in'

    def process(self):
        fields = []
        for field in self.dbf_connector.conn.fieldDefs:
            fields.append(field.name)
        for rec in self.dbf_connector.conn:
            data = {}
            for f in fields:
                data[f] = rec[f]
            yield data, 'main'

    def __getstate__(self):
        res = super(dbf_in, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(dbf_in, self).__setstate__(state)
        self.__dict__ = state

    def __copy__(self):
        res = dbf_in(self.dbfconnector ,self.name, self.transformer)
        return res

    def end(self):
        super(dbf_in, self).end()
        if self.dbf_connector:
            self.dbf_connector.close()
            self.dbf_connector = False

def test():
    from etl_test import etl_test
    import etl
    file_conn = etl.connector.dbf_connector('../../../demo/input/dbf_file.dbf')# /input/DE000446.dbf
    test = etl_test.etl_component_test(dbf_in(file_conn, name='dbf file test'))
    import datetime
    test.check_output([{'CUSTOMER': '1', 'REF': '0021', 'NAME': 'ASUStek'}, {'CUSTOMER': '1', 'REF': '0022', 'NAME': 'Agrolait'}, {'CUSTOMER': '0', 'REF': '0023', 'NAME': 'Distrib PC'}])
    res = test.output()

if __name__ == '__main__':
    test()
