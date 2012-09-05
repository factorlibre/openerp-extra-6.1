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
 To write data into open object model.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.component import component
import datetime

class openobject_out(component):
    """
    This is an ETL Component that writes data in open object model.

    Type                  : Data Component.
    Computing Performance : Streamline.
    Fields                : A mapping {OpenObject Field Name : Flow Name}.
    Input Flows           : 0-x.
    * .*                  : The main data flow with input data.
    Output Flows          : 0-1.
    * main                : Returns all data.
    """

    def __init__(self, openobject_connector, model, fields=None, openobject_id=None, name='component.output.openobject_out', transformer=None, row_limit=0):
        """
        Parameters
        openobject_connector : Open object connector to connect with OpenERP server.
        model                : Open object model name.

        Extra Parameters
        fields               : Fields of open object model.
        openobject_id        : if an id is supplied fill this field with the openerp id.
        name                 : Name of Component.
        transformer          : Transformer object to transform string data into particular object.
        """
        super(openobject_out, self).__init__(name=name, connector=openobject_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.openobject_out'
        self.model = model
        self.fields = fields
        self.openobject_id = openobject_id

    def __copy__(self):
        res = openobject_out(self.connector, self.model, self.fields, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(openobject_out, self).__getstate__()
        res.update({'fields':self.fields, 'model':self.model})
        return res

    def __setstate__(self, state):
        super(openobject_out, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        datas = []
        self.fields_keys = None
        self.op_oc = False
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not self.fields:
                        self.fields = dict(map(lambda x: (x, x), d.keys()))
                    if type(self.fields) == type([]):
                        self.fields_keys = self.fields
                        self.fields = dict(map(lambda x: (x, x), self.fields))
                    if not self.fields_keys:
                        self.fields_keys = self.fields.keys()
                    op_oc = self.connector.open()

                    l=(op_oc, 'execute', self.model, 'import_data', self.fields_keys, [map(lambda x: d[self.fields[x]], self.fields_keys)])
                    print "executing ",l
                    try:
                        r=self.connector.execute(*l)
                        print "got result",r
                    except Exception,e:
                        print "got exception",e
                        raise e
                    if r[0]==-1:
                        raise Exception(str(r))
                    if self.openobject_id and ('id' in self.fields):
                        word=d[self.fields['id']]
                        if '.' in word:
                            module, xml_id = word.rsplit('.',1)
                            s = [('module','=',module),('name','=',xml_id)]
                        else:
                            s = [('name','=',xml_id)]
                        l=(op_oc, 'execute', 'ir.model.data', 'search', s )
                        ids = self.connector.execute(*l)
                        if ids:
                            l=(op_oc, 'execute', 'ir.model.data', 'read',ids,['res_id'])
                            r=self.connector.execute(*l)
                            d[self.openobject_id]=r[0]['res_id']
                    self.connector.close(op_oc)
                    #print "imported data",d
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    openobject_conn = etl.connector.openobject_connector('http://localhost:8069', 'etl_test', 'admin', 'admin', con_type='xmlrpc')
    test = etl_test.etl_component_test(openobject_out(openobject_conn, 'res.country'))
    test.check_input({'main': [{'name': 'India_test', 'code':'India_test'}]})
    test.check_output([{'name': 'India_test', 'code':'India_test'}], 'main')
    res = test.output()

if __name__ == '__main__':
    test()

