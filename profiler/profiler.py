# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) Borja López Soilán <borja@kami.es>
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
"""
The OpenObject Profiler is a special module that tracks the execution of
the OpenObject server, and outputs several kinds of stats.
"""
__author__ = "Borja López Soilán <neopolus@kami.es>"
__date__ = "$05-abr-2011 20:48:57$"

from osv import orm
from osv import osv
import inspect
import time
import gc
import tools
import netsvc
import sys


#
# Note: As the profiler wraps some method calls, it makes the stack bigger:
#       Instead of one stack frame for each wrapped method, you'll
#       have two or three.
#       That means that the Python maximum recursion deep (usually 1000)
#       may be exceeded on recursive methods that previously were just
#       under the limit (for example ir.ui.menu._filter_visible_menus).
#
#       To prevent this, we raise the recursion limit a bit :)
#
sys.setrecursionlimit(2*sys.getrecursionlimit())


################################################################################
# Dictionaries to store the profiling data.
################################################################################

#
# Sample structure of the _service_methods_data dictionary:
#
#   _service_methods_data = {
#     'ir.attachment.search_count': { # Method data entry
#         'calls': 1,
#         'time': 0.0021409988403320312,
#         'orm_calls': {
#             'ir.attachment.search': { # ORM method data entry
#                 'calls': 1,
#                 'time': 0.0019710063934326172,
#                 'called_from': {
#                       'search@/opt/openerp/server-6.0/bin/addons/...
#                                           ...base/ir/ir_attachment.py:58': {
#                           'calls': 1,
#                           'time': 0.0019710063934326172,
#                       }
#                  }
#             }
#         }
#         'last_call_orm_trace': [
#               (0.00001992721558, 'ir.attachment.search', '/opt/openerp/...
#                  ...server-6.0/bin/addons/base/ir/ir_attachment.py:search:58')
#         ]
#         'browse_objects': {
#               'account.account': { 'created': 20366 }
#         }
#         'complexity': {
#             1: {
#                 'calls': 1,
#                 'time': 0.0019710063934326172,
#             }
#             10: {
#                 'calls': 1,
#                 'time': 0.0190000000000000000,
#             }
#         }
#     }
#   }
#
#
# Sample structure of the _orm_complexity_data dictionary:
#
# _orm_complexity_data = {
#   'ir.attachment.search': {
#       1: {
#           'calls': 1,
#           'time': 0.0019710063934326172,
#       }
#       10: {
#           'calls': 1,
#           'time': 0.0190000000000000000,
#       }
#   }
# }
#
#
# Sample structure of the _browse_records_data dictionary:
#
#   _browse_records_data = {
#        'account.account': { 'created': 20366, 'alive': 5016, 'garbage': 0 }
#   }
#

_service_methods_data = {}
_orm_complexity_data = {}
_browse_records_data = {}


# Dict to map cursors to method data records (to track the execution).
_cursor_to_service_method = {}




################################################################################
# Service methods profiling
################################################################################

def _profile_execute_cr(self, original_execute, cr, uid, model, method,
                        complexity_n, *args, **kwargs):
    """
    Calls and profiles the execute_cr method of the object_proxy class
    logging the elapsed time, complexity and other info.
    """
    #
    # Get the service data.
    #
    service_method = _service_methods_data\
                        .setdefault('%s.%s' % (model, method),
                                    {
                                        'calls': 0,
                                        'time': 0.0,
                                        'orm_calls': {},
                                        'last_call_orm_trace': None,
                                        'last_call_start': None,
                                        'browse_objects': {},
                                        'complexity': {}
                                    })
    complexity = service_method['complexity']\
                        .setdefault(complexity_n,
                                     {
                                        'calls': 0,
                                        'time': 0.0,
                                     })

    # Asociate the cursor with the service method, so orm methods can be
    # accounted on this service method.
    _cursor_to_service_method[cr] = service_method

    # Reset the call orm trace (we recreate it on each call):
    service_method['last_call_orm_trace'] = []
    service_method['last_call_start'] = time.time()

    #
    # Call (and benchmark) the original method.
    #
    start = time.time()
    return_value = original_execute(self, cr, uid, model, method,
                                    *args, **kwargs)
    stop = time.time()
    elapsed = stop - start

    #
    # Update the method counters.
    #
    service_method['calls'] += 1
    service_method['time'] += elapsed
    complexity['calls'] += 1
    complexity['time'] += elapsed

    # Unassociate the method data from the cursor.
    del _cursor_to_service_method[cr]

    return return_value


# Register our wrapper (monkey-patching the object_proxy class). ---------------

# Save the old method to call it later.
_old_execute = osv.object_proxy.execute_cr

def _execute_cr_wrapper(self, cr, uid, model, method, *args, **kwargs):
    """
    Wrapper for the execute_cr method of the object_proxy class.
    It parses some of the arguments, and then delegates on profile_execute_cr
    to do the real job.
    Finally dumps the logged data to a file.
    """
    complexity = 1
    if method in ('read', 'write', 'unlink'):
        complexity = len(args[0]) if isinstance(args[0], list) else int(args[0])
    elif method in ('search'):
        complexity = kwargs.get('limit', 0)

    res = _profile_execute_cr(self, _old_execute, cr, uid, model, method,
                                complexity, *args, **kwargs)


    # Dump the logged info.
    dump_data()

    return res

# Register our method (if it is not already registered).
if not hasattr(osv.object_proxy, 'profiler_enabled'):
    osv.object_proxy.profiler_enabled = True
    osv.object_proxy.execute_cr = _execute_cr_wrapper


################################################################################
# ORM methods profiling
################################################################################

def _profile_orm_method(self, original_method, cr, complexity_n,
                        *args, **kwargs):
    """
    Calls and profiles an orm method (in the context of a service method call)
    logging the elapsed time, complexity and other info.
    """
    orm_method_name = "%s.%s" % (self._name, original_method.__name__)
    service_method = _cursor_to_service_method.get(cr)
    orm_method = None

    #
    # Call (and benchmark) the original method.
    #
    start = time.time()
    return_value = original_method(self, *args, **kwargs)
    stop = time.time()
    elapsed = stop - start

    if service_method:
        #
        # Get the data to update.
        #
        orm_method = service_method['orm_calls']\
                            .setdefault(orm_method_name,
                                            {
                                                'calls': 0,
                                                'time': 0.0,
                                                'called_from': {}
                                            })
        complexity = orm_method.setdefault(complexity_n,
                                            {
                                                'calls': 0,
                                                'time': 0.0,
                                             })
        orm_meth_complex = _orm_complexity_data.setdefault(orm_method_name, {})
        orm_complexity = orm_meth_complex.setdefault(complexity_n,
                                            {
                                                'calls': 0,
                                                'time': 0.0,
                                             })

        #
        # Get the source of the call.
        #
        # Note: Each frame record is a tuple of six items:
        #           the frame object,
        #           the filename,
        #           the line number of the current line,
        #           the function name,
        #           a list of lines of context from the source code,
        #           and the index of the current line within that list.
        #
        frame = inspect.currentframe().f_back.f_back

        called_from_name = "%s@%s:%s" % (
                                            frame.f_code.co_name,
                                            frame.f_code.co_filename,
                                            frame.f_lineno
                                        )
        called_from = orm_method['called_from'].setdefault(called_from_name,
                                                            {
                                                                'calls': 0,
                                                                'time': 0.0,
                                                            })

        #
        # Update the counters.
        #
        orm_method['calls'] += 1
        orm_method['time'] += elapsed
        complexity['calls'] += 1
        complexity['time'] += elapsed
        orm_complexity['calls'] += 1
        orm_complexity['time'] += elapsed
        called_from['calls'] += 1
        called_from['time'] += elapsed

        #
        # Add the entry to the service method last call trace.
        #
        service_method['last_call_orm_trace'].append((
                            time.time() - service_method['last_call_start'],
                            orm_method_name,
                            called_from_name
                        ))

    return return_value




# Register our wrappers (monkey-patching the orm class). -----------------------


#
# Save the old methods to call them later.
#
_old_create = orm.orm.create
_old_read = orm.orm.read
_old_write = orm.orm.write
_old_unlink = orm.orm.unlink
_old_search = orm.orm.search

def _create_wrapper(self, *args, **kwargs):
    """Wrapper to profile the orm.create method."""
    return _profile_orm_method(self, _old_create, args[0], 1, *args, **kwargs)

def _read_wrapper(self, *args, **kwargs):
    """Wrapper to profile the orm.read method."""
    complexity_n = len(args[2]) if isinstance(args[2], list) else int(args[2])
    return _profile_orm_method(self, _old_read, args[0], complexity_n,
                                *args, **kwargs)

def _write_wrapper(self, *args, **kwargs):
    """Wrapper to profile the orm.write method."""
    complexity_n = len(args[2]) if isinstance(args[2], list) else int(args[2])
    return _profile_orm_method(self, _old_write, args[0], complexity_n,
                                *args, **kwargs)

def _unlink_wrapper(self, *args, **kwargs):
    """Wrapper to profile the orm.unlink method."""
    complexity_n = len(args[2]) if isinstance(args[2], list) else int(args[2])
    return _profile_orm_method(self, _old_unlink, args[0], 
                                complexity_n, *args, **kwargs)

def _search_wrapper(self, *args, **kwargs):
    """Wrapper to profile the orm.search method."""
    return _profile_orm_method(self, _old_search, args[0],
                                kwargs.get('limit', '0'), *args, **kwargs)

#
# Register our wrappers (if they are not already registered).
#
if not hasattr(orm.orm, 'profiler_enabled'):
    orm.orm.profiler_enabled = True
    orm.orm.create = _create_wrapper
    orm.orm.read = _read_wrapper
    orm.orm.write = _write_wrapper
    orm.orm.unlink = _unlink_wrapper
    orm.orm.search = _search_wrapper



################################################################################
# Browse record usage traking
################################################################################

def _refresh_offline_browse_object_counters():
    """
    Refreshes the counters of 'alive' and 'garbage' browse records,
    those counters are expensive to update on every call, so we only
    update them when this function is called.
    """
    alive_bos = [o for o in gc.get_objects() \
                    if isinstance(o, orm.browse_record)]
    garbage_bos = [o for o in gc.garbage if isinstance(o, orm.browse_record)]

    for bo_name, bo_data in _browse_records_data.iteritems():
        bo_data['alive'] = len([o for o in alive_bos \
                                    if o._table_name == bo_name])
        bo_data['garbage'] = len([o for o in garbage_bos \
                                        if o._table_name == bo_name])



# Register our wrappers (monkey-patching the browse record class). -------------

# Save the old methods to call them later.
_old_browse_record_init = orm.browse_record.__init__

def _browse_record_init_wrapper(self, cr, uid, oid, table, *args, **kwargs):
    service_method = _cursor_to_service_method.get(cr)
    if service_method:
        # Get the browse record local counters.
        browse_record = service_method['browse_objects']\
                                .setdefault(table._name, { 'created': 0 })
        # Update the counters.
        browse_record['created'] += 1

    # Get the browse record global counters.
    global_browse_record = _browse_records_data\
                                .setdefault(table._name,
                                            {
                                                'created': 0,
                                                'alive': 0,
                                                'garbage': 0,
                                            })
    # Update the counters.
    global_browse_record['created'] += 1

    return _old_browse_record_init(self, cr, uid, oid, table, *args, **kwargs)

#
# Register our wrapper (if it is not already registered).
#
if not hasattr(orm.browse_record, 'profiler_enabled'):
    orm.browse_record.profiler_enabled = True
    orm.browse_record.__init__ = _browse_record_init_wrapper









################################################################################
# Interface
################################################################################


def data_as_txt(sort_by='time'):
    """
    Creates an (almost) human-readable string with the info gathered by
    the profiler.

    Returns text that looks a bit like this:
    ---
       Service methods:
       Calls   Time                      Method
       1       0.0021409988403320312     ir.attachment.search_count
           ORM methods called:
               Calls   Time                      ORM Method
               1       0.0019710063934326172     ir.attachment.search
               Called from:
                   Calls   Time                     Source line
                   1       0.0019710063934326172    search@/opt/openerp/...
                        ...server-6.0/bin/addons/base/ir/ir_attachment.py:58
           ORM sample call trace:
               0.00001992721558: ir.attachment.search - search@/opt/openerp/...
                        ...server-6.0/bin/addons/base/ir/ir_attachment.py:58
           Browse Objects:
               Created     Model
               20366       account.account
       Browse Objects:
           Created    Alive       Garbage     Model
           20366      5016        0           account.account
    ---
    """

    def to_sorted_list(dict_to_sort, sort_by, asc=True):
        """
        Given a dictionary of dictionaries, returns a list of key-value tuples
        sorted by a given field of value.
        """
        def sortfunc(dict1, dict2):
            """
            Compares two dictionaries using the field given on the parent func.
            """
            diff = dict1[1][sort_by] - dict2[1][sort_by]
            if diff > 0:
                return 1 if asc else -1
            elif diff < 0:
                return -1 if asc else 1
            else:
                return 0
        items = [(key, value) for key, value in dict_to_sort.iteritems()]
        items.sort(sortfunc)
        return items

    #
    # Header.
    #
    buffer = ''
    buffer += '/' + '-' * 78 + '\\\n|\n'
    buffer += '| OpenObject Profiler Output\n|\n'
    buffer += '|' + '-' * 78 + '|\n'

    for service_method_name, service_method in \
                        to_sorted_list(_service_methods_data, sort_by, False):
        buffer += '|' + '-' * 78 + '|\n|\n'

        #
        # Service method name and counters.
        #
        buffer += '| Service method\n'
        buffer += '| %s\n|\n' % service_method_name
        buffer += '| Calls   Time      Time per call\n'
        tpc = service_method['time'] / service_method['calls'] \
                        if service_method['calls'] else 0
        buffer += '| %-8s%-10.9s%-10.9s\n' % (
                                        service_method['calls'],
                                        service_method['time'],
                                        tpc)

        #
        # ORM methods for the given service method.
        #
        buffer += "|\n|     ORM methods called (by the service method):\n"
        for orm_method_name, orm_method in \
                                    to_sorted_list(service_method['orm_calls'],
                                                   sort_by, False):
            #
            # ORM method name and counters.
            #
            buffer += "|       %s\n" % orm_method_name
            tpc = orm_method['time'] / orm_method['calls'] \
                        if orm_method['calls'] else 0
            buffer += "|       %-8s%-10.9s%-10.9s\n" % (
                                        orm_method['calls'],
                                        orm_method['time'],
                                        tpc)

            #
            # Called from details for the ORM method.
            #
            buffer += "|          Called from (callers of the ORM method):\n"
            for called_from_name, called_from_data in \
                                    to_sorted_list(orm_method['called_from'],
                                                    sort_by, False):
                # Source of the call.
                buffer += "|            %s\n" % called_from_name

                #
                # Counters for that source.
                #
                tpc = called_from_data['time'] / called_from_data['calls'] \
                            if called_from_data['calls'] else 0
                buffer += "|            %-8s%-10.9s%-10.9s\n" % (
                                        called_from_data['calls'],
                                        called_from_data['time'],
                                        tpc)

        #
        # Sample sequence of ORM calls for the given service method.
        #
        buffer += "|\n|     ORM sample call trace (for the service method):\n"
        for call_trace_line in service_method['last_call_orm_trace']:
            buffer += "|       %-11.11s: %s - %s\n" % (
                                        call_trace_line[0],
                                        call_trace_line[1],
                                        call_trace_line[2])

        #
        # Browse records of each kind created by the service method.
        #
        buffer += "|\n|     Browse Records (used by the service method):\n"
        buffer += "|       Created     Model\n"
        for browse_object_name, browse_object_data in \
                                to_sorted_list(service_method['browse_objects'],
                                'created', False):
            buffer += "|       %-12.11s%s\n" % (browse_object_data['created'],
                                                browse_object_name)

        #
        # Complexity of the service method.
        #
        buffer += "|\n|     Complexity profile " \
                                    "(records/items per service method call):\n"
        buffer += "|       Complex.    Time/item   " \
                                        "| Calls       Time        Time/call\n"
        complexities = list(service_method['complexity'].keys())
        complexities.sort()
        for complexity in complexities:
            complexity_data = service_method['complexity'][complexity]
            tpc = complexity_data['time'] / complexity_data['calls'] \
                        if complexity_data['calls'] else 0
            tpi = tpc / int(complexity) \
                    if complexity and int(complexity) else '-'
            buffer += "|       %-12.11s%-12.11s" \
                        "| %-12.11s%-12.11s%-12.11s\n" % (
                                                complexity or '-',
                                                tpi,
                                                complexity_data['calls'],
                                                complexity_data['time'],
                                                tpc)
        buffer += "|\n"
    
    #
    # Browse records of each kind created by the all the service methods.
    #
    buffer += '|' + '=' * 78 + '|\n|\n'
    buffer += "| Global Browse Records (used by all the service methods)\n|\n"
    buffer += "|       Created     Alive       Garbage     Model\n"
    for browse_object_name, browse_object_data in \
                        to_sorted_list(_browse_records_data, 'created', False):
        buffer += "|       %-12.11s%-12.11s%-12.11s%s\n" % (
                            browse_object_data['created'],
                            browse_object_data['alive'],
                            browse_object_data['garbage'],
                            browse_object_name)
    buffer += '|\n'

    #
    # Complexity of the ORM methods.
    #
    buffer += '|' + '=' * 78 + '|\n|\n'
    buffer += "| Global ORM complexity log " \
                                    "(records/items per orm method call)\n|\n"
    buffer += "|       Complex.    Time/item   " \
                                    "| Calls       Time        Time/call\n"
    for method_name, method_complexity_data in _orm_complexity_data.iteritems():
        buffer += "|       %s\n" % method_name
        complexities = list(method_complexity_data.keys())
        complexities.sort()
        for complexity in complexities:
            complexity_data = method_complexity_data[complexity]
            tpc = complexity_data['time'] / complexity_data['calls'] \
                        if complexity_data['calls'] else 0
            tpi = tpc / int(complexity) \
                        if complexity and int(complexity) else '-'
            buffer += "|       %-12.11s%-12.11s" \
                        "| %-12.11s%-12.11s%-12.11s\n" % (
                                                complexity or '-',
                                                tpi,
                                                complexity_data['calls'],
                                                complexity_data['time'],
                                                tpc)

    # Footer.
    buffer += '|\n'
    buffer += '\\' + '-' * 78 + '/\n'
    
    return buffer


def dump_data():
    """
    Dumps the logged data (translated into an human readable form,
    into the output file configured on the OpenERP config file
    ("profiler_output" key).
    """

    # Refresh the 'offline' counters before exporting the info.
    _refresh_offline_browse_object_counters()

    # Get the output as a string.
    txt_buffer = data_as_txt()

    #
    # Write the output file
    #
    if tools.config.get('profiler_output'):
        with open(tools.config['profiler_output'], 'w') as f:
            f.write(txt_buffer)
    else:
        print txt_buffer



#
# Warn if the output has not been defined.
#
logger = netsvc.Logger()
msg = "Profiler enabled."
logger.notifyChannel('addons.profiler', netsvc.LOG_INFO, msg)
if not tools.config.get('profiler_output'):
    msg = "No profiler_output defined in config file!"
    msg += " (Using standard output)"
    logger.notifyChannel('addons.profiler', netsvc.LOG_WARNING, msg)
else:
    msg = "Using %s as output file." % tools.config['profiler_output']
    logger.notifyChannel('addons.profiler', netsvc.LOG_INFO, msg)