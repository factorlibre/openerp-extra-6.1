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
 To read data from csv file incoming from http://www.meilleuregestion.com/


 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.component import component
from etl.component.input.csv_in import csv_in

class meilleuregestion_csv_in(csv_in):
    """
    This is an ETL Component that is used to read data from csv file. Its type is data component.
    Its computing peformance is streamline.
    It has two flows
        Input Flows    : 0.
        * .*           : Nothing.
        Output Flows   : 0-x.
        * .*           : Returns the main flow with data from csv file.
    """

    def __init__(self, fileconnector, csv_params={}, name='component.input.csv_in', transformer=None, row_limit=0):
        """
        Required  Parameters
        fileconnector   : Localfile connector.

        Extra Parameters
        name            : Name of Component.
        transformer     : Transformer object to transform string data into  particular object.
        row_limit       : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        csv_param       : To specify other csv parameter like fieldnames , restkey , restval etc.
        """
        super(csv_in, self).__init__(name=name, connector=fileconnector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.meilleuregestion_csv_in'
        self.csv_params = csv_params
        self.csv_params['delimiter'] =';'
        


    def process(self):
        if self.is_end():
            self.warning('No any Output attached')
        import csv
        self.fp = self.connector.open()
        reader = csv.DictReader(self.fp, **self.csv_params)
        #Skip the 2 first header lines
        reader.next()
        reader.next()

        l = []
        #Read data untill CUMUL line is reach
        for data in reader:
            if data:
                if data[None] != ['CUMUL']:
                    for i in range(len(data[None])):
                        l.append((i,data[None][i].decode('raw_unicode_escape')))
                    data = dict(l)

                    yield data, 'main'
                else:
                    break

def test():
    from etl_test import etl_test
    import etl
    file_conn = etl.connector.localfile('../../../demo/input/partner1.csv')
    test = etl_test.etl_component_test(csv_in(file_conn, name='csv test'))
    test.check_output([{'tel': '+32.81.81.37.00', 'id': '11', 'name': 'Fabien'}])
    res = test.output()
    print res

if __name__ == '__main__':
    test()
