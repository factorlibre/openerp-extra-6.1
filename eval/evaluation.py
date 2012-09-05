# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
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

from osv import osv, fields
import time
import tools
from tools import to_xml
from mx import DateTime as dt
import pooler
from tools.translate import _


class hr_evaluation(osv.osv):
    _name = "hr.evaluation"
    _description = "Evaluation"

    def button_cancel(self, cr, uid, ids, context):
        eval_form_obj = self.pool.get('hr.evaluation.form')
        for form_eval in self.browse(cr, uid, ids)[0].eval_form_ids:
            if form_eval.state == 'draft':
                eval_form_obj.write(cr, uid, [form_eval.id], {'state': 'cancel'}, context)
        self.write(cr, uid, ids, {'state': 'cancel'}, context)
        return True

    def button_done(self, cr, uid, ids, context):
        evaluation_obj = self.pool.get('hr.evaluation')
        setting_obj = self.pool.get('hr.evaluation.setting')
        answ_obj = pooler.get_pool(cr.dbname).get('hr.evaluation.values')
        eval_form_obj = self.pool.get('hr.evaluation.form')
        users_obj = self.pool.get('res.users')
        criteria_obj = self.pool.get('hr.evaluation.criteria')
        curr_employee = evaluation_obj.browse(cr, uid, ids)[0].employee_id
        setting_id = []
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr, uid, [('parent_id', '=', curr_employee.id)])
        mail_send = users_obj.browse(cr, uid, uid).address_id
        email_from = mail_send and mail_send.email or None
        subject = 'Notification for Evaluation'
        body = 'Please fill forms of evaluation!'
        employee_ids.append(curr_employee.id)
        if curr_employee.parent_id:
            employee_ids.append(curr_employee.parent_id.id)
        for evaluation in evaluation_obj.browse(cr, uid, ids):
            for employee in employee_obj.browse(cr, uid, employee_ids):
                ## ADdd criteria basing on products
                new_criteria_ids = []
                prdct_id = employee.product_id.id
                if prdct_id:
                    setting_id = setting_obj.search(cr, uid, [('product_id', '=', prdct_id)])
                    if setting_id:
                        setting_ids = setting_obj.browse(cr, uid, setting_id)
                        for set_id in setting_ids:
                            for crit in set_id.criteria_ids:
                               # new_criteria_ids.append(criteria_obj.copy(cr, uid, crit.id,{}))
                                new_criteria_ids.append(crit.id)
               # for crit in  curr_employee.grid_id.criteria_ids:
               #     new_criteria_ids.append(criteria_obj.copy(cr, uid, crit.id,{'grid_id':False}))
                if not setting_id:
                    raise osv.except_osv(_('Error'), _('Please set a job that defines setting to your employee "%s"!') % (employee.name or ''))

                mail_emp = self.browse(cr, uid, employee).user_id
                email_to = mail_emp and mail_emp.address_id and mail_emp.address_id.email or None
                if email_to:
                    tools.email_send(email_from, email_to, subject, body, None)
                eval_id = eval_form_obj.create(cr, uid, {
                                    'name': evaluation.name + ((evaluation.next_eval and'/' + evaluation.next_eval) or ''),
                                    'employee_id': evaluation.employee_id.id,
                                    'employee_id2': employee.id,
                                    'eval_id': evaluation.id,
                                    'state': 'draft',
                                    'setting_id': setting_id and setting_id[0] or None,
           #                         'criteria_ids':[(6,0, new_criteria_ids)]
                                    }, context)
                item = eval_form_obj.browse(cr, uid, eval_id)
                for crit in new_criteria_ids:
                    answ_obj.create(cr, uid, {'employee_id': item.employee_id.id,
                                            'criteria_id': crit,
                                            'form_id': eval_id,
                                    })
        self.write(cr, uid, ids, {'state': 'pending'})

        return True

    def action_done(self, cr, uid, ids, context=None):
        for eval_id in self.browse(cr, uid, ids, context=context):
            t = [i.state == 'draft' for i in eval_id.eval_form_ids]
            if len(t):
                return False
        self.write(cr, uid, ids, {'state': 'done'}, context)

        return True

    def button_update(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'updated'}, context)
        return True

    _columns = {
        'name': fields.char('Evaluation Name', size=64, translate=True, required=True),
        'next_eval': fields.date('Next Evaluation', select="1"),
        'employee_id': fields.many2one('hr.employee', 'Employee', select=True, required=True),
        'eval_form_ids': fields.one2many('hr.evaluation.form', 'eval_id', 'Evaluations Forms'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('pending', 'Pending'),
            ('updated', 'Salary Updated'),
            ('cancel', 'Canceled')], 'State', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.evaluation'),
    }

hr_evaluation()


class hr_evaluation_section(osv.osv):
    _name = "hr.evaluation.section"
    _description = "Evaluation Section"
    _columns = {
        'name': fields.char('Evaluation Section', size=64, required=True, select=True),
        'code': fields.char('code', size=64, select = True),
        'active': fields.boolean('active'),
    }
    _defaults = {
        'active': lambda *a: True,
    }

hr_evaluation_section()


class hr_evaluation_criteria(osv.osv):
    _name = "hr.evaluation.criteria"
    _description = "Evaluation Criteria"
    _columns = {
        'name': fields.char('Name of criteria', size=128, translate=True, required=True),
        'desc_criteria': fields.text('Description of criteria', translate=True),
        'rating': fields.selection([('weak', 'Weak'),
                                    ('good', 'Good'),
                                    ('very_good', 'Very Good'),
                                    ('excellent', 'Excellent'),
                                    ('no_advice', 'No Advice')], 'Rating'),
        'active': fields.boolean('Active'),
        'format_text': fields.boolean('Format Text'),
        'format_select': fields.boolean('Format Selection'),
        'section_id': fields.many2one('hr.evaluation.section', 'Section', select=True),
        'text_criteria': fields.char('Text Criteria', size=64),
        'sequence': fields.integer('Sequence'),
    }

    _defaults = {
        'active': lambda *a: True,
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the criteria must be unique !')
    ]

    def create(self, cr, uid, vals, context=None):
        if not vals['format_text'] and not vals['format_select']:
            raise osv.except_osv(_('Error'), _('Please select format select or format text!'))
        return super(hr_evaluation_criteria, self).create(cr, uid, vals, context)

hr_evaluation_criteria()


class hr_evaluation_setting(osv.osv):
    _name = "hr.evaluation.setting"
    _description = "Setting Evaluation Form"
    _columns = {
        'name': fields.char('Evaluation Name', size=64, translate=True, required=True),
        'criteria_ids': fields.many2many('hr.evaluation.criteria', 'setting_id', 'crit_id', 'set_id', 'List of Criteria'),
        'product_id': fields.many2one('product.product', 'Job', select=True),
    }

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        if context.get('set', None) == 'my':
            cr.execute("""select distinct s.id from hr_evaluation_setting s, hr_evaluation_form f, hr_employee e,
                          res_users r where f.setting_id = s.id and f.employee_id2 = e.id and
                          r.id = %s and e.user_id=r.id""", [uid])
            res = cr.fetchall()
            ids = [r[0] for r in res]
        return super(hr_evaluation_setting, self).read(cr, uid, ids, fields, context, load)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        eval_form_obj = self.pool.get('hr.evaluation.form')
        if view_type == 'form':
            res = super(hr_evaluation_form, eval_form_obj).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        res = super(hr_evaluation_setting, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        return res

hr_evaluation_setting()


class hr_evaluation_form(osv.osv):
    _name = "hr.evaluation.form"
    _description = "Evaluation Form"

    def button_show(self, cr, uid, ids, context):
        if context is None:
            context = {}
        setting_id = self.browse(cr, uid, ids[0]).setting_id.id
        context.update({'setting_id': setting_id})
        return {
                'res_id': ids[0],
                'type':'ir.actions.act_window',
                'view_id': False,
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'hr.evaluation.form',
                'context': context,
                }

    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
        if context is None:
            context = {}
        result = super(hr_evaluation_form, self).fields_get(cr, uid, fields, context)
        setting_obj = self.pool.get('hr.evaluation.setting')
        groups = self.pool.get('hr.evaluation.setting').search(cr, uid, [])
        groups_br = self.pool.get('hr.evaluation.setting').browse(cr, uid, groups)
        # XXX to translate:
        result['name'] = {'string': _('Name'), 'type': 'char', 'size': 64, 'required': True}
        result['state'] = {'string': _('State'), 'type': 'selection', 'selection': [('draft', 'Draft'),
                                                                                 ('cancel', 'Cancel'),
                                                                                 ('done', 'Done'),
                                                                                 ('review', 'Reviewed by top management')]}
        result['note'] = {'string': _('Note'), 'type': 'text'}
        result['employee_id'] = {'string': _('Employee'), 'type': 'many2one', 'relation': 'hr.employee'}
        result['setting_id'] = {'string': _('Setting'), 'type': 'many2one', 'relation': 'hr.evaluation.setting', 'required': True}
        result['employee_id2'] = {'string': _('Employee that evaluates'), 'type': 'many2one', 'relation': 'hr.employee'}
        setting_id = context.get('active_id', False)
        if not setting_id:
            setting_id = context.get('setting_id', False)
        if setting_id:
            for g in setting_obj.browse(cr, uid, setting_id).criteria_ids:
                result['val_q_%d' % g.id] = {'string': 'Comment %s' % g.name, 'type': 'text'}
                result['rating_%d' % g.id] = {'string': 'Rating %s' % g.name, 'type': 'selection', 'selection': [('nothing', ''),
                                                                                                                ('weak', 'Weak'),
                                                                                                                ('good', 'Good'),
                                                                                                                ('very_good', 'Very Good'),
                                                                                                                ('excellent', 'Excellent'),
                                                                                                                ('no_advice', 'No Advice')]}
                result['crit_%d' % g.id] = {'string': '%s' % g.name, 'type': 'many2one', 'relation': 'hr.evaluation.criteria'}
                result['form_%d' % g.id] = {'string': '%s' % g.name, 'type': 'many2one', 'relation': 'hr.evaluation.form'}
        return result

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        result = super(hr_evaluation_form, self).search(cr, uid, args, offset, limit, order, context, count)
        user_id = context.get('uid', None)
        setting_id = context.get('setting_id', None)
        states = context.get('states', None)
        if user_id and setting_id and states:
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and r.id=%s and f.employee_id2 = e.id and
                          f.setting_id = %s and f.state in %s""", [user_id, setting_id, tuple(states)])
            return [a[0] for a in cr.fetchall()]
        elif states and user_id:
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and f.states in %s and
                          f.employee_id2 = e.id and r.id = %s""", [tuple(states), setting_id])
        elif states and setting_id:
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and f.state in %s and
                          f.employee_id2 = e.id and f.setting_id = %s""", [tuple(states), setting_id])
            return [a[0] for a in cr.fetchall()]
        elif user_id and setting_id:
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and r.id=%s and f.employee_id2 = e.id and
                          f.setting_id = %s""", [user_id, setting_id])
            return [a[0] for a in cr.fetchall()]
        elif setting_id:
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and f.employee_id2 = e.id and
                          f.setting_id = %s""", [setting_id])
            return [a[0] for a in cr.fetchall()]
        elif user_id:
            user_id = uid
            cr.execute("""select f.id from hr_evaluation_form f, hr_employee e, res_users r
                          where e.user_id=r.id and r.id=%s and
                          f.employee_id2 = e.id""", [user_id])
            return [a[0] for a in cr.fetchall()]

        return result

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        for grid in self.browse(cr, uid, ids, context=context):
            model_id = grid.id
            perms_rel = ['form_id', 'criteria_id', 'text_criteria', 'rating', 'employee_id']
        setting_id = context.get('active_id', False)
        if not setting_id:
            setting_id = context.get('setting_id', False)
        acc_obj = self.pool.get('hr.evaluation.values')
        set_obj = self.pool.get('hr.evaluation.setting')
        crit_obj = self.pool.get('hr.evaluation.criteria')
        states = context.get('state', None)
        user_id = context.get('uid', None)
        set_id = context.get('set', None)
        if states and user_id:
            ids = self.search(cr, uid, [('state', 'in', [states]), ('create_uid', '=', uid)], context=context)
        elif states:
            ids = self.search(cr, uid, [('state', 'in', [states])], context=context)
        result = super(hr_evaluation_form, self).read(cr, uid, ids, fields, context, load)
        if not isinstance(result, list):
            result = [result]
        if setting_id:
            for res in result:
                current_setting = set_obj.browse(cr, uid, setting_id)
                for crit in current_setting.criteria_ids:
                    rules = acc_obj.search(cr, uid, [('form_id', '=', res['id']), ('criteria_id', '=', crit.id)])
                    rules_br = acc_obj.browse(cr, uid, rules, context=context)
                    for rule in rules_br:
                        res['id'] = rule.form_id.id
                        res['val_q_%d' % crit.id] = rule.val_question
                        res['rating_%d' % crit.id] = rule.rating
        return result

    def create(self, cr, uid, vals, context=None):
        res = super(hr_evaluation_form, self).create(cr, uid, vals, context)
        for key, value in vals.items():
            if key.startswith('form_') or key.startswith('crit_'):
                del vals[key]
        self.write(cr, uid, [res], vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        setting_id = context and context.get('setting_id', context.get('active_id')) or False
        acc_obj = self.pool.get('hr.evaluation.values')
        crit_obj = self.pool.get('hr.evaluation.criteria')
        set_obj = self.pool.get('hr.evaluation.setting')
        for grid in self.browse(cr, uid, ids, context=context):
            rules = []
            model_id = grid.id
            perms_rel = ['form_id', 'criteria_id', 'text_criteria', 'rating', 'employee_id']
            for val in vals:
                if not setting_id or (not val.startswith('val_q_') and not val.startswith('rating_')):
                    res = super(hr_evaluation_form, self).write(cr, uid, ids, {val: vals[val]}, context)
                    continue
            #current_setting = set_obj.browse(cr, uid, setting_id)
            current_setting = set_obj.browse(cr, uid, grid.setting_id.id)
            for crit in current_setting.criteria_ids:
                data_new = {}
                rules = acc_obj.search(cr, uid, [('form_id', '=', grid.id), ('criteria_id', '=', crit.id)])
                if not rules:
                    data_new.update({
                     'form_id': grid.id,
                     'employee_id': vals.get('employee_id'),
                     'val_question': vals.get('val_q_%d'%crit.id),
                     'rating': vals.get('rating_%d'%crit.id),
                     'criteria_id': crit.id})
                    rule_id = [acc_obj.create(cr, uid, data_new)]
                else:
                    rules_br = acc_obj.browse(cr, uid, rules, context=context)
                    for rule in rules_br:
                        for val in vals:
                            if 'rating_' == val[0:7]:
                                if rule.criteria_id.id == int(val[7:]):
                                    data_new['rating'] = vals[val]
                                    acc_obj.write(cr, uid, [rule.id], data_new, context=context)
                            elif 'val_q_' == val[0:6]:
                                if rule.criteria_id.id == int(val[6:]):
                                    data_new['val_question'] = vals[val]
                                    acc_obj.write(cr, uid, [rule.id], data_new, context=context)

        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        if context is None:
            context = {}
        setting_obj = self.pool.get('hr.evaluation.setting')
        values_obj = self.pool.get('hr.evaluation.values')
        sett_obj = self.pool.get('hr.evaluation.setting')
        criteria_obj = self.pool.get('hr.evaluation.criteria')
        values_ids = values_obj.search(cr,uid,[])
        res = {}
        setting_id = context.get('active_id', False)
        if not setting_id:
            setting_id = context.get('setting_id', False)
        cols = ['criteria_id', 'form_id', 'text_criteria', 'rating']
        flag='y'
        r_only = 1
        has_group = [x.name for x in self.pool.get('res.users').browse(cr,uid,uid).groups_id if x.name=='Human Resources / Manager']
        if has_group:
            r_only = 0
        section_name = ''
        if (view_type =='form'):
            res['arch'] = """<?xml version="1.0"?>
                <form string="Evaluation Form">
                <field name="name" select = "1"/>
                <field name="employee_id" select = "1" readonly = "%d"/>
                <field name="setting_id" select = "2" readonly = "%d" />
                <field name="employee_id2" select = "2" readonly = "%d"/>
                <newline/>
                <notebook colspan = "4">
            """%(r_only, r_only, r_only)
            _Section_list = []
            set_ids = []
            if setting_id:
                for field in setting_obj.browse(cr,uid, setting_id).criteria_ids:
                    _tmp_list = []
                    _tmp_list_id = []
                    set_ids = []
                    seq = []
                    if (field.section_id and field.section_id.name) not in _Section_list:
                        _Section_list.append(field.section_id and field.section_id.name)
                        _tmp_list.append(field.section_id and field.section_id.name)
                        _tmp_list_id.append(field.section_id and field.section_id.id)
                    if _tmp_list:
                        for i in setting_obj.browse(cr, uid, setting_id).criteria_ids:
                            if i.section_id:
                                if i.section_id.id == _tmp_list_id[0]:
                                    set_ids.append(i.id)
                                    seq.append((i.sequence,i.id))
                        first_page = res['arch'].find('<page')
                        last_page = res['arch'].find('</page>')
                        if first_page != -1:
                            res['arch'] +="""</page>"""
                            res['arch'] += """
                                <page string="%s">"""%(field.section_id and field.section_id.name or '')
                        if flag == 'y':
                            flag = ''
                            res['arch'] += """
                                <page string="%s">"""%(field.section_id and field.section_id.name or '')
                    res['arch']+="""
                        """
                    set_ids = [l[1] for l in seq if l]
                    for field in criteria_obj.browse(cr,uid, set_ids):
                        if field.active:
                            res['arch']+="""<group col="1" colspan="2">
                                            <separator colspan="2" string="%s"/>
                                            <label string="%s" align="0.0"/>
                                            """%(to_xml(field.name),to_xml(field.desc_criteria or ''),)
                            if field.format_text:
                                res['arch'] += """<field name="val_q_%d" nolabel="1"/>
                                                <newline/>
                                                """%(field.id)
                            if field.format_select:
                                res['arch'] += """<label string="Rating" align="0.0"/>
                                                <newline/>"""
                                res['arch'] += """<field name="rating_%d" nolabel="1"/>"""%(field.id)
                            res['arch'] += """</group>"""
            first_page = res['arch'].find('<page')
            last_page = res['arch'].find('</page>')
            if not res['arch'].endswith('</page>') and (first_page!=-1) :
                res['arch'] +="""</page>"""
            res['arch'] += """</notebook>
                    <separator colspan="4" string="Note"/>
                    <field name="note"  colspan="4" nolabel = "1"/>
            """
            res['arch'] += """ <group colspan="4" col="5" >
                    <field name="state" select="1" readonly="1"/>
                    <button name="button_done" string="Con_firm" type="object" states="draft" />
                    <button name="button_cancel" string="Can_cel" type="object"  states="draft,done,review"/>
                    <button name="button_review" string="Re_viewed by top management" type="object" states="done"/>
                     </group>"""
            res['arch'] += "</form>"
            res['fields'] = self.fields_get(cr, uid, cols, context)
        else:
            res = super(hr_evaluation_form,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        return res

    def button_review(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'review'}, context)
        return True

    def button_cancel(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'cancel'}, context)
        return True

    def button_done(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'done'}, context)
        evaluation_obj = self.pool.get('hr.evaluation')
        form_id = self.browse(cr, uid, ids)[0]
        eval_id = form_id and form_id.eval_id
        if eval_id and eval_id.eval_form_ids:
            eval_states = [x.id for x in eval_id.eval_form_ids if x.state != 'done']
            if not len(eval_states):
                evaluation_obj.write(cr, uid, eval_id.id, {'state': 'done'})
        return True

    _columns = {
        'name': fields.char('Evaluation Name', size=64, translate=True, required=True),
        'note': fields.char('Notice', size=128, select = True),
        'send_date': fields.date('Sending/Creation Date'),
        'employee_id': fields.many2one('hr.employee', 'Employee', select=True),
        'employee_id2': fields.many2one('hr.employee', 'Employee that evaluates', select=True),
        'setting_id': fields.many2one('hr.evaluation.setting', 'Setting', select=True),
        'eval_id': fields.many2one('hr.evaluation', 'Employee that evaluates', select=True, ondelete='cascade'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('cancel', 'Cancel'),
                                   ('done', 'Done'),
                                   ('review', 'Reviewed by top management')], 'State', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'send_date': lambda *a: time.strftime('%Y-%m-%d'),

    }

hr_evaluation_form()


class hr_skill_level(osv.osv):
    _name = "hr.skill.level"
    _description = "Skill Level"

    _columns = {
        'name': fields.char('Skill Name', size=64, required=True, select=True),
        'code': fields.char('Code', size=64, select=True),
        'active': fields.boolean('Active'),
        'desc_skill': fields.text('Skill Description'),
    }
    _defaults = {
        'active': lambda *a: True,
    }

hr_skill_level()


class hr_evaluation_grid(osv.osv):
    _name = "hr.evaluation.grid"
    _description = "Evaluation Grid"

    def _ratio1(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for rec in self.browse(cr, uid, ids):
            result[rec.id] = (1+(0.01*(rec.ratio or 0.0))) * rec.salary
        return result

    def _ratio2(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for rec in self.browse(cr, uid, ids):
            result[rec.id] = (1-(0.01*(rec.ratio or 0.0))) * rec.salary
        return result

    def _ratio(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for rec in self.browse(cr, uid, ids):
            result[rec.id] = rec.salary_market != 0 and (rec.salary/rec.salary_market)*100 or 0.0
        return result

    def _current_salary(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, 0)
        for id in ids:
            cr.execute("""SELECT grid_id, rate FROM hr_grid_rate WHERE
                          grid_id = %s  ORDER BY date_rate desc LIMIT 1""", [id])
            if cr.rowcount:
                id, rate = cr.fetchall()[0]
                res[id] = rate
        return res

    _columns = {
        'name': fields.char('Code', size=64, required = True, select = True),
        'active': fields.boolean('active'),
        'salary': fields.function(_current_salary, method=True, string='Current Salary', digits=(12, 2)),
        'ratio': fields.float(string='Ratio'),
        'ratio1': fields.function(_ratio1, string='Maximum', method=True),
        'ratio2': fields.function(_ratio2, string='Minimum', method=True),
        'percent_ratio': fields.function(_ratio, string='Ratio', method=True),
        'salary_market': fields.float('Salary/Market'),
        'rate_ids': fields.one2many('hr.grid.rate', 'grid_id', 'Rates'),
    }

    _defaults = {
        'active': lambda *a: True,
    }

hr_evaluation_grid()


class hr_evaluation_history(osv.osv):
    _name = "hr.evaluation.history"

    def _variance(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.old_grid_id.salary_market != 0 and (100*rec.old_salary/rec.old_grid_id.salary_market) or 0.0
        return result

    def _ratio(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.salary_market != 0 and (100*rec.old_salary/rec.salary_market) or 0.0
        return result

    _description = "Evaluation History for the Employee"
    _columns = {
        'date_eval': fields.date('Evaluation Date'),
        'old_salary': fields.float('Old Salary'),
        'old_grid_id': fields.many2one('hr.evaluation.grid', 'Old Level/Grid', select=True, required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', select=True),
        'salary_market': fields.float('Updated Salary'),
    }

hr_evaluation_history()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def running_nexteval_dates(self, cr, uid, *args):
        evaluation_obj = pooler.get_pool(cr.dbname).get('hr.evaluation')
        eval_hist_obj = pooler.get_pool(cr.dbname).get('hr.evaluation.history')
        employee_obj = pooler.get_pool(cr.dbname).get('hr.employee')
        employee_ids = employee_obj.search(cr, uid, [])
        for emp in employee_obj.browse(cr, uid, employee_ids):
            if not len(emp.history_ids):
                #USE date on contract instead of date defined on the employee
                cr.execute("""select date_start from hr_contract where employee_id = %s and
                              (date_end >= %s or date_end is NULL) order by date_start desc""", [emp.id, time.strftime('%Y-%m-%d')])
                last_date = cr.fetchone()
                last_date = last_date and last_date[0] or None
              #  last_date=emp.date_entry or None
              #  salary_market=emp.grid_id and emp.grid_id.salary_market or 0.0
                old_grid_id = emp.grid_id.id or None
                old_salary = emp.current_salary or 0.0
            else:
                cr.execute("""select max(date_eval),old_grid_id,old_salary from hr_evaluation_history
                              where employee_id=%s group by old_grid_id,old_salary""", [emp.id])
                res = cr.fetchone()
                last_date = res and res[0] or None
                old_grid_id = res and res[1] or None
                old_salary = res and res[2] or 0.0

            if last_date and (dt.ISO.ParseAny(last_date)+dt.RelativeDateTime(months=+6, days=-15)).strftime('%Y-%m-%d') == dt.now().strftime('%Y-%m-%d'):
                eval_hist_obj.create(cr, uid, {'employee_id': emp.id,
                                            'date_eval': (dt.ISO.ParseAny(last_date)+ dt.RelativeDateTime(months=+6)).strftime('%Y-%m-%d'),
                                            'old_grid_id': old_grid_id,
#                                            'salary_market':salary_market,
                                            'old_salary': old_salary
                })
                evaluation_obj.create(cr, uid, {'employee_id': emp.id,
                                            'next_eval': (dt.ISO.ParseAny(last_date)+ dt.RelativeDateTime(months=+6)).strftime('%Y-%m-%d'),
                })
        return True

    def _curr_salary(self, cr, uid, ids, field_name, arg, context):
        result = {}
        contract_obj = self.pool.get('hr.contract')
        eval_hist_obj = self.pool.get('hr.evaluation.history')
        s = 0.0
        for rec in self.browse(cr, uid, ids):
            contract_id = contract_obj.search(cr, uid, [('employee_id', '=', rec.id)])
            if contract_id:
                for rec1 in contract_obj.browse(cr, uid, contract_id):
                    if not rec.history_ids and (rec1.date_start <= time.strftime('%Y-%m-%d') and (not rec1.date_end or rec1.date_end >= time.strftime('%Y-%m-%d'))):
                        s = rec1.wage or 0.0
                    else:
                        employ_id = eval_hist_obj.search(cr, uid, [('employee_id', '=', rec.id)])
                        if employ_id:
                            s = eval_hist_obj.browse(cr, uid, employ_id)[0].salary_market or 0.0
            result[rec.id] = s
        return result

    _columns = {
        'skill_id': fields.many2one('hr.skill.level', 'Skill Description', select=True),
        'grid_id': fields.many2one('hr.evaluation.grid', 'Grid', select=True),
        'date_entry': fields.date('Date Entry'),
        'current_salary': fields.function(_curr_salary, string='Salary', method=True, help = "Is the current salary"),
        'history_ids': fields.one2many('hr.evaluation.history', 'employee_id', 'Evaluations History'),
        'product_id': fields.many2one('product.product', 'Job', select=True),

    }
    _defaults = {
    }

hr_employee()


class hr_grid_rate(osv.osv):
    _name = "hr.grid.rate"
    _description = "Grid Rates"
    _rec_name = 'rate'
    _columns = {
        'rate': fields.float('Rate', select=True),
        'date_rate': fields.date('Date'),
        'active': fields.boolean('active'),
        'grid_id': fields.many2one('hr.evaluation.grid', 'Grid', select=True),
    }
    _defaults = {
        'active': lambda *a: True,
        'date_rate': lambda *a: time.strftime('%Y-%m-%d'),
    }

hr_grid_rate()


class hr_evaluation_values(osv.osv):
    _name = "hr.evaluation.values"
    _description = "Evaluation values"
    _columns = {
        'criteria_id': fields.many2one('hr.evaluation.criteria', 'Criteria', select=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', select=True),
        'rating': fields.selection([('nothing', ''), ('weak', 'Weak'), ('good', 'Good'), ('very_good', 'Very Good'), ('excellent', 'Excellent'), ('no_advice', 'No Advice')], 'Rating'),
        'val_question': fields.char('Value of the question', size= 64),
        'text_criteria': fields.char('Text Criteria', size=64),
        'form_id': fields.many2one('hr.evaluation.form', 'Evaluation', select= True)
    }

hr_evaluation_values()

