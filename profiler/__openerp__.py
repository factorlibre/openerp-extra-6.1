# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) Borja López Soilán <neopolus@kami.es>
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
{
    "name" : "OpenObject Profiler",
    "version" : "0.1",
    "author" : "NeoPolus",
    "category": 'Development tools',
    "description": """OpenObject service and ORM profiler.
    
'A profiler is a program that describes the run time performance of a program
 providing a variety of statistics' - (James Roskind, Python Docs)

The OpenObject Profiler is a special module that tracks the execution of
the OpenObject server, and outputs several kinds of stats like:
    * Number of service level calls (from an OpenObject client) and time spent.
    * ORM methods called by the service layer (times, sources of calls...).
    * Complexity info for service and ORM methods (time by number of records
      processed).
    * Browse records usage on the service methods (and leakage info).

A text output file will be created with a summary of the logged data after
each service level call (after each client operation). The file name can be
configured by setting the 'profiler_output' option on the OpenObject server
configuration file.

Warning: This module shouldn't be installed on a production database!
         It's a tool made by developers for developers and developers only!



This is a sample of the output of the profiler:

/------------------------------------------------------------------------------\
|
| OpenObject Profiler Output
|
|------------------------------------------------------------------------------|
|------------------------------------------------------------------------------|
|
| Service method
| ir.ui.menu.read
|
| Calls   Time      Time per call
| 186     0.6144866 0.0033036
|
|     ORM methods called (by the service method):
|       ir.ui.menu.read
|       186     0.6038930 0.0032467
|          Called from (callers of the ORM method):
|            execute_cr@.../bin/osv/osv.py:167
|            186     0.6038930 0.0032467
|       ir.ui.menu.search
|       141     0.1454751 0.0010317
|          Called from (callers of the ORM method):
|            search@.../bin/addons/base/ir/ir_ui_menu.py:107
|            141     0.1454751 0.0010317
|       res.users.read
|       140     0.1129667 0.0008069
|          Called from (callers of the ORM method):
|            read@.../bin/addons/base/res/res_user.py:267
|            140     0.1129667 0.0008069
|
|     ORM sample call trace (for the service method):
|       0.001493930: ir.ui.menu.search - search@.../base/ir/ir_ui_menu.py:107
|       0.002168893: res.users.read - read@.../base/res/res_user.py:267
|       0.002876043: ir.ui.menu.read - execute_cr@...bin/osv/osv.py:167
|
|     Browse Records (used by the service method):
|       Created     Model
|       1314        ir.ui.menu
|
|     Complexity profile (records/items per service method call):
|       Complex.    Time/item   | Calls       Time        Time/call
|       1           0.003345962 | 70          0.234217405 0.003345962
|       2           0.001361489 | 1           0.002722978 0.002722978
|       3           0.001032924 | 100         0.309877395 0.003098773
|       8           0.000580956 | 9           0.041828870 0.004647652
|       9           0.000478519 | 6           0.025840044 0.004306674
|
|==============================================================================|
|
| Global Browse Records (used by all the service methods)
|
|       Created     Alive       Garbage     Model
|       1314        109         0           ir.ui.menu
|
|==============================================================================|
|
| Global ORM complexity log (records/items per orm method call)
|
|       Complex.    Time/item   | Calls       Time        Time/call
|       res.users.read
|       1           0.000814499 | 190         0.154754877 0.000814499
|       ir.ui.menu.read
|       1           0.003299624 | 70          0.230973720 0.003299624
|       2           0.001343965 | 1           0.002687931 0.002687931
|       3           0.001018521 | 148         0.452223539 0.003055564
|       5           0.000274610 | 2           0.002746105 0.001373052
|       8           0.000576370 | 9           0.041498661 0.004610962
|       9           0.000474298 | 6           0.025612115 0.004268685
|       21          0.001669777 | 3           0.105195999 0.035065333
|       38          0.000126301 | 3           0.014398336 0.004799445
|       77          0.000353303 | 3           0.081613063 0.027204354
|       78          0.000162627 | 3           0.038054943 0.012684981
|       ir.ui.menu.search
|       -           -           | 191         0.204602479 0.001071217
|
\------------------------------------------------------------------------------/

""",
    'website': 'http://www.kami.es',
    'init_xml': [],
    "depends" : [],
    'update_xml': [],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
