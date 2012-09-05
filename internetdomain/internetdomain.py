# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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

from osv import osv, fields
from tools.translate import _
from tools import config

import time
import datetime
import netsvc

class internetdomain_domain(osv.osv):
    def _date_expire_days_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            cr.execute("select max(date_expire) as exp_date from internetdomain_renewal where domain_id=%s", (rec.id,))
            res = cr.dictfetchone()
            result[rec.id] = res and res['exp_date'] or False
        return result

    def _warning_expire(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = False

            intdomain_alert_expire = rec.company_id.intdomain_alert_expire
            if not intdomain_alert_expire:
                max_alert = 30 #30 days
            else:
                intdomain_alert_expire = intdomain_alert_expire.split(',')
                intdomain_alert_expire = [int(x) for x in intdomain_alert_expire]
                max_alert = intdomain_alert_expire[0]
                for x in intdomain_alert_expire:
                    if x > max_alert:
                        max_alert = x

            if rec.date_expire:
                today = datetime.date.today()
                date_exp = datetime.date(int(rec.date_expire[:4]), int(rec.date_expire[5:7]), int(rec.date_expire[8:]))
                diff_date = datetime.timedelta()
                diff_date = date_exp - today
                if diff_date.days <= max_alert:
                    result[rec.id] = True
        return result

    def run_mail_scheduler(self, cr, uid, use_new_cursor=False, context=None):
        company_ids = self.pool.get('res.company').search(cr, uid, [])
        for company_id in company_ids:
            company = self.pool.get('res.company').browse(cr, uid, company_id)
            intdomain_alert_expire = company.intdomain_alert_expire
            if not intdomain_alert_expire:
                days_alert = [30] #30 days
            else:
                days_alert = intdomain_alert_expire.split(',')
                days_alert = [int(x) for x in days_alert]
            for day in days_alert:
                cr.execute("select domain_id from internetdomain_renewal as a LEFT JOIN internetdomain_domain AS b ON b.id = a.domain_id where a.date_expire=%s AND b.company_id = %s AND b.active = True", (datetime.date.today()+datetime.timedelta(days=day),company_id))
                res = cr.dictfetchall()
                ids = [r['domain_id'] for r in res]
                for domain in self.browse(cr, uid, ids, context):
                    template = domain.company_id.intdomain_template
                    logger = netsvc.Logger()
                    if not template.id:
                        logger.notifyChannel(_("Internet Domain"), netsvc.LOG_ERROR, _("Not template configurated. Configure your company template or desactive Scheduled Actions"))
                        return False
                    else:
                        logger.notifyChannel(_("Internet Domain"), netsvc.LOG_INFO, _("Send email domain: %s") % domain.name)
                        self.pool.get('poweremail.templates').generate_mail(cr, uid, template.id, [domain.id])
        return True

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = False
        contact_addr_id = False

        if partner_id:
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'default'])
            contact_addr_id = res['default']

        result = {'value': {
            'partner_address_id': contact_addr_id,
            }
        }
        return result

    _name = 'internetdomain.domain'
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'date_create': fields.date('Create', required=True),
        'date_expire': fields.function(_date_expire_days_get, method=True, type="date", string="Date expired"),
        'warning_expire': fields.function(_warning_expire, method=True, type="boolean", string="Warning expired"),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'partner_address_id': fields.many2one('res.partner.address', 'Partner Contact', domain="[('partner_id','=',partner_id)]", required=True),
        'registrator_id': fields.many2one('res.partner', 'Registrator', required=True),
        'registrator_website':fields.related('registrator_id', 'website', type='char', size=64, string='Website'),
        'dns1': fields.char('DNS Primary', size=100),
        'dns2': fields.char('DNS Secundary', size=100),
        'dns3': fields.char('DNS Secundary (2)', size=100),
        'dns4': fields.char('DNS Secundary (3)', size=100),
        'ip': fields.char('IP', size=100),
        'comments': fields.text('Comments'),
        'active': fields.boolean('Active'),
        'renewal_ids': fields.one2many('internetdomain.renewal', 'domain_id', string='Renewals'),
        'product_ids': fields.many2many('product.product','interdomain_product_rel','domain_id','product_id','Products'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'network_id': fields.many2one('network.network','Network'),
    }

    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]

    _defaults = {
        'active': lambda *a: 1,
        'company_id': _default_company,
    }
internetdomain_domain()

class internetdomain_renewal(osv.osv):
    def onchange_registrator_id(self, cr, uid, ids, domain_id):
        if not domain_id:
            return {'value':{'registrator_id': False}}
        value = self.pool.get('internetdomain.domain').browse(cr, uid, domain_id).registrator_id.id
        data = {'registrator_id':value} 
        return {'value':data}
    
    _name = "internetdomain.renewal"
    _description = "Renewals"
    _columns = {
        'domain_id': fields.many2one('internetdomain.domain','Domain', required=True),
        'registrator_id': fields.many2one('res.partner', 'Registrator', required=True),
        'date_renewal': fields.date('Date', required=True),
        'date_expire': fields.date('Expire', required=True),
        'price_unit': fields.float('Unit Price', required=True),
        'comments': fields.text('Comments'),
    }
    _defaults = {
        'date_renewal': lambda *a: time.strftime('%Y-%m-%d'),
    }

internetdomain_renewal()
