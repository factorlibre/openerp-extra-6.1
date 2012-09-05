# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import os
import netsvc
import pooler
import pydot
import tools
import report
import unicodedata


# a small monkey patch to patch a bug in pydot:
def needs_quotes(s):
    """If the string is one of the reserved keywords it will need quotes too."""
    # If any of these regexes match, then the string does not need quoting
    if (pydot.id_re_alpha_nums.match(s) or pydot.id_re_num.match(s) or
            pydot.id_re_dbl_quoted.match(s) or pydot.id_re_html.match(s) or
            pydot.id_re_with_port.match(s)):
        return False

    return True

pydot.needs_quotes = needs_quotes


def translate_accent(text):
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore')


def graph_get(cr, uid, graph, offer_id):
    pool = pooler.get_pool(cr.dbname)
    # Get user language:
    user_lang = get_user_lang(cr, uid)
    context = {'lang': user_lang}

    trans_obj =  pool.get('ir.translation')
    offer_obj = pool.get('dm.offer')
    step_type = pool.get('dm.offer.step.type')

    offer = offer_obj.browse(cr, uid, offer_id, context=context)[0]
    nodes = {}
    type_ids = step_type.search(cr, uid, [])
    for step in offer.step_ids:
        if not step.graph_hide:
            args = {}

            # Get Code Translation:
            type_trans = trans_obj._get_ids(cr, uid, 'dm.offer.step,code', 'model', user_lang, [step.id])
            type_code = type_trans[step.id] or step.code
            args['label'] = translate_accent(type_code +'\\n' + step.media_id.code)

            graph.add_node(pydot.Node(step.id, **args))

    tr_ids = trans_obj.search(cr, uid, [('name', '=', 'dm.offer.step.transition.trigger,name')])
    trs = trans_obj.browse(cr, uid, tr_ids, context=context)

    for step in offer.step_ids:
        for transition in step.outgoing_transition_ids:
            if not transition.graph_hide:
                trargs = {
                    'label': translate_accent(transition.condition_id.name + '\\n' + str(transition.delay) + ' ' + transition.delay_type),
                    'arrowtail': 'inv',
                }
                graph.add_edge(pydot.Edge( str(transition.step_from_id.id), 
                        str(transition.step_to_id.id), fontsize="10", **trargs))
    return True


def get_user_lang(cr, uid):
    usr_obj = pooler.get_pool(cr.dbname).get('res.users')
    user = usr_obj.browse(cr, uid, [uid])[0]
    return user.context_lang or 'en_US'


class report_graph_instance(object):
    def __init__(self, cr, uid, ids, data):
        logger = netsvc.Logger()
        try:
            import pydot
        except Exception, e:
            logger.notifyChannel('workflow', netsvc.LOG_WARNING,
                'Import Error for pydot, you will not be able \
                                                        to render workflows\n'
                'Consider Installing PyDot or dependencies: \
                                                http://dkbza.org/pydot.html')
            raise e
        offer_id = ids
        self.done = False

        offer = translate_accent(pooler.get_pool(cr.dbname).get('dm.offer').browse(cr, uid, offer_id)[0].name)

        graph = pydot.Dot(fontsize="16", label=offer, size='10.7, 7.3',
                          center='1', ratio='auto', rotate='90', rankdir='LR' )

        graph_get(cr, uid, graph, offer_id)

        ps_string = graph.create_ps(prog='dot')
        if os.name == "nt":
            prog = 'ps2pdf.bat'
        else:
            prog = 'ps2pdf'
        args = (prog, '-', '-')
        try:
            _input, output = tools.exec_command_pipe(*args)
        except:
            return
        _input.write(ps_string)
        _input.close()
        self.result = output.read()
        output.close()
        self.done = True

    def is_done(self):
        return self.done

    def get(self):
        if self.done:
            return self.result
        else:
            return None

class report_graph(report.interface.report_int):
    def __init__(self, name, table):
        report.interface.report_int.__init__(self, name)
        self.table = table

    def result(self):
        if self.obj.is_done():
            return (True, self.obj.get(), 'pdf')
        else:
            return (False, False, False)

    def create(self, cr, uid, ids, data, context={}):
        self.obj = report_graph_instance(cr, uid, ids, data)
        return (self.obj.get(), 'pdf')

report_graph('report.dm.offer.graph', 'dm.offer')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
