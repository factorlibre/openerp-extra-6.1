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
 To display log detail in streamline.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
import pprint, sys, time

from etl.component import component
class logger(component):
    """
        This is an ETL Component that use to display log detail in streamline.

	    Type                   : Data Component.
		Computing Performance  : Streamline.
		Input Flows            : 0-x.
		* .*                   : The main data flow with input data.
		Output Flows           : 0-y.
		* .*                   : Returns the main flow.
    """
    def __init__(self, output=sys.stdout, name='component.transfer.logger'):
        super(logger, self).__init__(name=name)
        self._type = 'component.transfer.logger'
        self.output = output

    def __getstate__(self):
        res = super(logger, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(logger, self).__setstate__(state)
        self.__dict__ = state

    def __copy__(self):
        res = logger(self.output, self.name)
        return res

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    #self.output.write('%s %s\n%s\n'%(time.strftime("%Y-%m-%d %H:%M:%S "),self.name,pprint.pformat(d)))
                    #self.output.flush()
                    self.output.write('%s %s (%s rows)\n'%(time.strftime("%Y-%m-%d %H:%M:%S "),self.name,len(d)))
                    yield d, 'main'

