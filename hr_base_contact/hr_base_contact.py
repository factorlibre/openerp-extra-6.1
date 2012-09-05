# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields, osv
from tools.translate import _

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    _columns = {
        'contact_id': fields.many2one('res.partner.contact', 'Contact'),
    }

    def create(self, cr, uid, vals, context):
        employee_id = super(hr_employee, self).create(cr, uid, vals, context)
        contact_id = self.create_contact_relation(cr, uid, employee_id, context)
        return employee_id

    def create_contact_relation(self, cr, uid, employee_id, context=None):
        if not context:
            context={}
        employee = self.browse(cr, uid, employee_id, context=context)
        contact_obj = self.pool.get('res.partner.contact')
        partner_job_obj = self.pool.get('res.partner.job')
        if not employee['address_id']:
            raise osv.except_osv(_('Error'),
                 _('In order to link this employee with a contact, you must enter a work address first.'))
        email = employee.work_email
        contact_ids = contact_obj.search(cr, uid, [('email', '=', email),('email', '!=', False)], context=context)
        if not contact_ids:
            contact_fullname = employee.name.split(' ')
            if len(contact_fullname) > 1:
                first_name = contact_fullname.pop(0)
                name = " ".join(contact_fullname)
            else:
                first_name = ''
                name = contact_fullname[0]
            values = {
                'name': name,
                'first_name': first_name,
                'email': email,
            }
            contact_id = contact_obj.create(cr, uid, values, context=context)
            values = {
                'address_id': employee['address_id'].id,
                'contact_id': contact_id,
            }
            partner_job_id = partner_job_obj.create(cr, uid, values, context=context)
        else:
            for contact_id in contact_ids:
                values = {
                    'address_id': employee['address_id'].id,
                    'contact_id': contact_id,
                }
                partner_job_id = partner_job_obj.create(cr, uid, values, context=context)
        self.write(cr, uid, [employee_id], {'contact_id': contact_id}, context=context)
        return contact_id

hr_employee()
