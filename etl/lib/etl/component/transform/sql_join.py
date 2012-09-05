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
 To read data from SQL database.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component
from etl.connector import sql_connector
import datetime

class sql_join(component):
    """
    This is an ETL Component that is used to join data from SQL database to the current data

    Type                  : Data Component.
    Computing Performance : Streamline.
    Input Flows           : 0.
    * .*                  : Nothing.
    Output Flows          : 0-x.
    * .*                  : Returns the main flow with data from csv file.
    """

    def __init__(self, sqlconnector, sqlquery, joinkey, name='component.input.sql_join', outputkey=False, transformer=None):

        """
        Required Parameters
        sqlconnector  : SQLconnector connector.
        sqlquery      : SQL Query
        joinkey       : join key

        Extra Parameters
        name          : Name of Component.
        outputkey     : Key of the data that will contain the result of query
        transformer   : Transformer object to transform string data into particular type.
        """
        super(sql_join, self).__init__(name=name, connector=sqlconnector, transformer=transformer,)
        self._type = 'component.input.sql_join'
        self.sqlquery = sqlquery
        self.joinkey = joinkey
        self.outputkey = outputkey and outputkey or joinkey


    def __copy__(self):
        res = sql_join(self.connector, self.sqlquery, self.joinkey, self.name, self.transformer)
        return res

    def end(self):
        super(sql_join, self).end()
        if self.sql_con:
            self.connector.close(self.sql_con)
            self.sql_con = False

    def __getstate__(self):
        res = super(sql_join, self).__getstate__()
        res.update({'sqlquery':self.sqlquery,'sql_joinkey':self.joinkey})
        return res

    def __setstate__(self, state):
        super(sql_join, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        self.sql_con = self.connector.open()
        cursor = self.sql_con.cursor()

        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    query = self.sqlquery % (d[self.joinkey])
                    print 'query', query
                    cursor.execute(query)
                    rows = cursor.fetchone()
                    print 'rows', rows
                    if not rows:
                        raise 'Result of the Query is False. Query: ' + str(query)
                    d.update({self.outputkey: rows[0]}) 
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    sql_conn = etl.connector.sql_connector('localhost', 5432, 'trunk', 'postgres', 'postgres')
    query =  'select * from etl_test'# execute the query you wish to
    test = etl_test.etl_component_test(sql_join(sql_conn, query))
    test.check_output([{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}])# output according to the executed query should be written over here.
    res = test.output()
    print res

if __name__ == '__main__':
    test()
