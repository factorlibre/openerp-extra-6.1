# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
import time

from report import report_sxw

class module_test_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(module_test_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_state_msg' : self.get_state_msg,
            'get_check_certi': self.get_check_certi,
            'get_data':self.get_data,
            'get_certificate_state':self.get_certificate_state,
        })

    def get_certificate_state(self,state_name):
        if state_name == 'not_started':
            result =  'Not Started'
        elif state_name == 'failed':
            result = 'Failed'
        elif state_name == 'succeeded':
            result = 'Succeeded'
        elif state_name == 'skipped':
            result = 'Skipped'
        else:
            result = ''
        return result

    def get_state_msg(self, state, cert_no):
        state_string = ''
        if state=='done':
            state_string = '''Congratulations, your module has succesfully succedded our quality tests. Find here the  certificate number of this module: %s

Please note it carefully, we strongly recommend you to even to integrate it into the __terp__.py file of your module  because it may be asked for any help on migration process. \n\n'''%cert_no
        elif state=='failed':
            state_string = '''Unfortunately, your module didn't succeed our quality tests. Please find below the reasons of this failure. \n\n'''
        return state_string

    def get_check_certi(self, tech_cert, func_cert):
        certificate_string = ''
        if not tech_cert:
            certificate_string += '''Please note that, as requested from your side, the certificaiton process was only based on the functional quality tests. Tiny sprl disclaims any liability for failure resulting from a technical bug and for maintenance matters.\n\n'''
        if not func_cert:
            certificate_string += '''Please note that, as requested from your side, the certificaiton process was only based on the technical quality tests. Tiny sprl disclaims any liability for failure resulting from a functional bug or error analysis.'''
        return certificate_string

    def get_data(self, line_ids):
        category_list = []
        value_list = []
        cmp_gp = {}
        result = []
        for line in line_ids:
            res = {}
            res['category'] = line.template_id.category_id.name
            res['name'] = line.template_id.name
            res['status'] = line.template_id.importance
            res['remark'] = line.remark
            res['value'] = line.template_id.add_value
            if len(result):
                if (line.template_id.category_id.name in category_list) and (line.template_id.add_value in value_list):
                    for r in result:
                        if(r['category'] == line.template_id.category_id.name) and (r['value'] == line.template_id.add_value):
                            result[result.index(r)]['name'] = result[result.index(r)]['name']+", "+ str(line.template_id.name)
                            result[result.index(r)]['remark'] = result[result.index(r)]['remark']+", "+str(line.remark)
                        else:
                            continue
                elif (line.template_id.category_id.name in category_list):
                    res['category'] = ''
                    result.append(res)
                else:
                    result.append(res)
            else:
                result.append(res)
            if line.template_id.category_id.name not in category_list:
                category_list.append(line.template_id.category_id.name)
            if line.template_id.add_value not in value_list:
                value_list.append(line.template_id.add_value)
        cnt_cate = 1
        for r in result:
            cnt = 1
            if result[result.index(r)]['category']:
                result[result.index(r)]['category'] = str(cnt_cate)+". "+"Test Category: "+result[result.index(r)]['category']
                result[result.index(r)]['name'] = str(cnt)+") "+"Test: "+result[result.index(r)]['name']
                cnt_cate = cnt_cate + 1
            else:
                cnt = cnt + 1
                result[result.index(r)]['name'] = str(cnt)+") "+"Test: "+result[result.index(r)]['name']
        return result

report_sxw.report_sxw('report.maintenance.module.test','maintenance.maintenance.module','addons/maintenance_editor/report/module_test.rml',parser=module_test_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: