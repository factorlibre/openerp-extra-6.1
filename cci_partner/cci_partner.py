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

import re
import time

from osv import fields, osv
import netsvc
from tools.translate import _

def check_phone_num(self, cr, uid, id, phone):
    if not phone:
        return {}
    result = {}
    gsm_num = ['0470','0471','0472','0473','0474','0475','0476','0477','0478','0479','0484','0485','0486','0487','0488','0489','0492','0493','0494','0495','0496','0497','0498','0499']
    if not phone.startswith('00'):
        is_gsm = False
        for item in gsm_num:
            is_gsm = phone.startswith(item)
            if is_gsm:
                break
        if is_gsm:
            if not len(phone) == 10:
                raise osv.except_osv(_('Validate Error'),
                    _('Invalid GSM Phone number. Only 10 figures numbers are allowed.'))
        else:
            if not len(phone) == 9:
                raise osv.except_osv(_('Validate Error'),
                    _('Invalid Phone number. Only 9 figures numbers are allowed.'))
    result['phone'] = phone
    return {'value': result}


class res_company(osv.osv):
    _inherit = 'res.company'
    _description = 'res.company'

    def _get_default_ad(self, addresses):
        city = post_code = address = country_code = ''
        for ads in addresses:
            if ads.type == 'default':
                if ads.zip_id:
                    city = ads.zip_id.city
                    post_code = ads.zip_id.name
                if ads.street:
                    address = ads.street
                if ads.street2:
                    address += ads.street2
                if ads.country_id:
                    country_code = ads.country_id.code
        return city, post_code, address, country_code

    _columns = {
        'federation_key' : fields.char('ID for the Federation',size=50,help="ID key for the sending of data to the belgian CCI's Federation"),
    }

res_company()

class res_partner_reason(osv.osv):
    _name = "res.partner.reason"
    _description = 'res.partner.reason'
    _columns = {
        'name': fields.char('Reason', size=50, required=True, select="1"),
    }
res_partner_reason()

class res_partner_state2(osv.osv):
    _name = "res.partner.state2"
    _description = 'res.partner.state2'
    _columns = {
        'name': fields.char('Customer Status',size=50,required=True),
    }
res_partner_state2()

class res_partner_article_review(osv.osv):
    _name = "res.partner.article.review"
    _description = 'res.partner.article.review'
    _columns = {
        'name': fields.char('Name',size=50, required=True),
        'date':fields.date('Date', required=True),
        'article_ids':fields.one2many('res.partner.article','review_id','Articles'),
    }

    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d')
    }

res_partner_article_review()


class res_partner_article(osv.osv):
    _name = "res.partner.article"
    _description = 'res.partner.article'
    _rec_name = 'article_id'
    _columns = {
        'article_id': fields.char('Article',size=256),
        'page':fields.integer('Page',size=16),
        'article_length':fields.float('Length'),
        'picture':fields.boolean('Picture'),
        'data':fields.boolean('Data'),
        'graph':fields.boolean('Graph'),
        'summary':fields.text('Summary'),
        'source_id':fields.char('Source',size=256),
        'date':fields.date('Date', required=True),
        'title':fields.char('Title',size=250, required=True),
        'subtitle':fields.text('Subtitle'),
        'press_review':fields.boolean('In the next press review',help='Must be inserted on the next press review'),
        'canal_id':fields.char('Reference',size=200,help='A text with or without a link incorporated'),
        'review_id':fields.many2one('res.partner.article.review','Review'),
        'partner_ids':fields.many2many('res.partner','res_partner_article_rel','article_id','partner_id','Partners'),
        'contact_ids':fields.many2many('res.partner.contact','res_partner_contact_article_rel', 'article_id','contact_id','Contacts'),
    }
    _defaults = {
                 'press_review' : lambda *a: False,
                 'article_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner.article'),
                 }
res_partner_article()

class res_partner_article_keywords(osv.osv):
    _name = "res.partner.article.keywords"
    _description = 'res.partner.article.keywords'
    _columns = {
        'name': fields.char('Name',size=80,required=True),
        'article_ids':fields.many2many('res.partner.article','partner_article_keword_rel','keyword_id','article_id','Articles'),
    }
res_partner_article_keywords()


class res_partner_article(osv.osv):
    _inherit = "res.partner.article"
    _columns = {
        'keywords_ids':fields.many2many('res.partner.article.keywords','article_keyword_rel','article_id','keyword_id','Keywords'),
    }
res_partner_article()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = "res.partner"

    def create(self, cr, uid, vals, *args, **kwargs):
        if vals.has_key('vat') and vals['vat']:
            vals.update({'vat':vals['vat'].upper()})
        new_id = super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
        #complete the user_id (salesman) automatically according to the zip code of the main address. Use res.partner.zip to select salesman according to zip code
        if vals.has_key('address') and vals['address']:
            for add in vals['address']:
                if add[2]['zip_id'] and add[2]['type']=='default':
                    data=self.pool.get('res.partner.zip').browse(cr, uid, add[2]['zip_id'])
                    saleman_id = data.user_id.id
                    self.write(cr,uid,[new_id],{'user_id':saleman_id})
        return new_id

    def write(self, cr, uid, ids,vals, context=None):
        list=[]
        if vals.has_key('vat') and vals['vat']:
            vals.update({'vat':vals['vat'].upper()})
        for partner in self.browse(cr, uid, ids):
            if not partner.user_id:
        #if not self.pool.get('res.partner').browse(cr, uid, ids)[0].user_id.id:
                if 'address' in vals:
                    for add in vals['address']:
                        if add[2] and (add[2]['zip_id'] and add[2]['type']=='default'):
                            data=self.pool.get('res.partner.zip').browse(cr, uid, add[2]['zip_id'])
                            saleman_id = data.user_id and data.user_id.id or False
                            if saleman_id:
                                if context and ('__last_update' in context):
                                    del context['__last_update']
                                self.write(cr,uid,[partner.id],{'user_id':saleman_id},context=context)
        return super(res_partner,self).write(cr, uid, ids,vals, context)


    def check_address(self, cr, uid, ids):
        #constraints to ensure that there is only one default address by partner.
        data_address=self.browse(cr, uid, ids)
        list=[]
        for add in data_address[0].address:
            if add.type in list and add.type=='default':
                return False
            list.append(add.type)
        return True

    def _check_activity(self,cr,uid,ids):
        data_partner=self.browse(cr, uid, ids)
        for data in data_partner:
            list_activities = []
            for activity in data.activity_code_ids:
                list_activities.append((activity.importance, activity.activity_id.list_id))
            main_list = []
            for (importance, list_id) in list_activities:
                if importance == "main":
                    if list_id in main_list:
                        return True#TODO: return False
                    main_list.append(list_id)
        return True

    def _get_customer_state(self, cr, uid, ctx):
        ids = self.pool.get('res.partner.state2').search(cr, uid, [('name','like', 'Imputable')])
        if ids:
            return ids[0]
        return False

    def _get_followup_level(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            cr.execute('select l.id from account_followup_followup_line l left join account_move_line ml on (ml.followup_line_id=l.id) where ml.partner_id = %s order by l.sequence DESC limit 1' % (rec.id))
            r = cr.fetchone ()
            result[rec.id] = r and r[0] or False
        return result

    def _salesman_search(self, cr, uid, ids, field_name, args, context={}):
        if not len(args):
          return []

        operator = args[0][1]
        value = args[0][2]
        u_ids= self.pool.get('res.users').search(cr,uid,[('name', operator, value)])
        p_ids= self.pool.get('res.partner').search(cr,uid,[('user_id', 'in' , u_ids)])
        if not p_ids:
          return [('id','=','0')]
        return [('id','in',p_ids)]


    def _get_salesman(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.user_id and rec.user_id.id or False
        return result


    _columns = {
        'employee_nbr': fields.integer('Nbr of Employee (Area)',help="Nbr of Employee in the area of the CCI"),
        'employee_nbr_total':fields.integer('Nbr of Employee (Tot)',help="Nbr of Employee all around the world"),
        'invoice_paper':fields.selection([('transfert belgian','Transfer belgian'),('transfert iban','Transfer iban'),('none','No printed transfert')], 'Bank Transfer Type', size=32),
        'invoice_public':fields.boolean('Invoice Public'),
        'invoice_special':fields.boolean('Invoice Special'),
        'state_id2':fields.many2one('res.partner.state2','Customer State',help='status of the partner as a customer'),
        'reason_id':fields.many2one('res.partner.reason','Reason'),
        'activity_description':fields.text('Activity Description',translate=True),
        'activity_code_ids':fields.one2many('res.partner.activity.relation','partner_id','Activity Codes'),
        'export_procent':fields.integer('Export(%)'),
        'export_year':fields.date('Export date',help='year of the export_procent value'),
        'import_procent':fields.integer('Import (%)'),
        'import_year':fields.date('Import Date',help='year of the import_procent value'),
        'invoice_nbr':fields.integer('Nbr of invoice to print',help='number of additive invoices to be printed for this customer'),
        'name_official':fields.char('Official Name',size=80),
        'name_old':fields.char('Former Name',size=80),
        'wall_exclusion':fields.boolean('Not in Walloon DB',help='exclusion of this partner from the walloon database'),
        #'mag_send':fields.selection([('never','Never'),('always','Always'),('managed_by_poste','Managed_by_Poste'),('prospect','Prospect')], 'Send mag.'),
        'date_founded':fields.date('Founding Date',help='Date of foundation of this company'),
        'training_authorization':fields.char('Checks Auth.',size=12,help='Formation and Language Checks Authorization number'),
        'alert_advertising':fields.boolean('Adv.Alert',help='Partners description to be shown when inserting new advertising sale'),
        'alert_events':fields.boolean('Event Alert',help='Partners description to be shown when inserting new subscription to a meeting'),
        'alert_legalisations':fields.boolean('Legal. Alert',help='Partners description to be shown when inserting new legalisation'),
        'alert_membership':fields.boolean('Membership Alert',help='Partners description to be shown when inserting new ship sale'),
        'alert_others':fields.boolean('Other alert',help='Partners description to be shown when inserting new sale not treated by _advertising, _events, _legalisations, _Membership'),
        'alert_explanation':fields.text('Warning'),
        'dir_name':fields.char('Name in Member Dir.',size=250,help='Name under wich the partner will be inserted in the members directory'),
        'dir_name2':fields.char('1st Shortcut name ',size=250,help='First shortcut in the members directory, pointing to the dir_name field'),
        'dir_name3':fields.char('2nd Shortcut name ',size=250,help='Second shortcut'),
        'dir_date_last':fields.date('Partner Data Date',help='Date of latest update of the partner data by itself (via paper or Internet)'),
        'dir_date_accept':fields.date("Good to shoot Date",help='Date of last acceptation of Bon a Tirer'),
        'dir_presence':fields.boolean('Dir. Presence',help='Present in the directory of the members'),
        'dir_date_publication':fields.date('Publication Date'),
        'dir_exclude':fields.boolean('Dir. exclude',help='Exclusion from the Members directory'),

        'country_relation':fields.one2many('res.partner.country.relation','partner_id','Country Relation'),
        'address': fields.one2many('res.partner.address', 'partner_id', 'Addresses'),# overridden just to change the name with "Addresses" instead of "Contacts"
        'relation_ids' : fields.one2many('res.partner.relation','current_partner_id','Partner Relation'),
        'canal_id': fields.many2one('res.partner.canal', 'Favourite Channel'),
        'followup_max_level': fields.function(_get_followup_level, method=True, type='many2one', relation="account_followup.followup.line", string="Max. Followup Level"),
        'article_ids' : fields.many2many('res.partner.article','res_partner_article_rel','partner_id','article_id','Articles'),
        'badge_partner':fields.char('Badge Partner',size=128),
        'user_id_readonly': fields.function(_get_salesman, fnct_search=_salesman_search, method=True, string='Salesman', type='many2one', relation='res.users'),
        'write_date' : fields.datetime('Last Modification'),
        'write_uid' : fields.many2one('res.users','Last Modifier',help='The last person who has modified this address'),
        #Never,Always,Managed_by_Poste,Prospect

        #virement belge,virement iban
        }
    _defaults = {
        'wall_exclusion' : lambda *a: False,
        'dir_presence' : lambda *a: False,
        'dir_exclude':lambda *a: False,
        'state_id2': _get_customer_state,
        'invoice_special' :lambda *a: 1,
        }
    _constraints = [(check_address, 'Only One default address is allowed!', ['address']),(_check_activity, 'Partner Should have only one Main Activity!', ['activity_code_ids'])]

    _sql_constraints = [
        ('vat_uniq', 'unique (vat)', 'The VAT of the partner must be unique !')
    ]

res_partner()

class res_partner_zip_group_type(osv.osv):
     _name = "res.partner.zip.group.type"
     _description = 'res.partner.zip.group.type'
     _columns = {
         'name':fields.char('Name',size=50,required=True),
                }
res_partner_zip_group_type()

class res_partner_zip_group(osv.osv):
     _name = "res.partner.zip.group"
     _description = 'res.partner.zip.group'
     _columns = {
         'type_id':fields.many2one('res.partner.zip.group.type','Type'),
         'name':fields.char('Name',size=50,required=True),
                }
res_partner_zip_group()

class res_partner_zip(osv.osv):
    _name = "res.partner.zip"
    _description = 'res.partner.zip'
    def check_group_type(self, cr, uid, ids):
        data=self.browse(cr, uid, ids)
        for id in ids:
            sql = '''
            select group_id from partner_zip_group_rel1 where zip_id=%d
            ''' % (id)
            cr.execute(sql)
            groups = cr.fetchall()
        list_group=[]
        for group in groups:
            list_group.append(group[0])
        data_zip = self.pool.get('res.partner.zip.group').browse(cr, uid,list_group)
        list_zip=[]
        for data in data_zip:
            if data.type_id.id in list_zip:
                return False
            list_zip.append(data.type_id.id)
        return True

    def name_get(self, cr, user, ids, context={}):
        #will return zip code and city......
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','city']):
            zip_city = str(r['name'] or '')
            if r['name'] and r['city']:
                zip_city += ' '
            r['city'] = r['city'].encode('utf-8')
            zip_city += str(r['city'] or '')
            res.append((r['id'], zip_city))
        return res

    _constraints = [(check_group_type, 'Error: Only one group of the same group type is allowed!', ['groups_id'])]
    _columns = {
        'name':fields.char('Zip Code',size=10,required=True, select=1),
        'city':fields.char('City',size=60,translate=True, required=True),
        'partner_id':fields.many2one('res.partner','Master Cci'),
        'post_center_id':fields.char('Post Center',size=40),
        'post_center_special':fields.boolean('Post Center Special'),
        'user_id':fields.many2one('res.users','Salesman Responsible'),
        'groups_id': fields.many2many('res.partner.zip.group', 'partner_zip_group_rel1', 'zip_id', 'group_id', 'Areas'),
        'distance':fields.integer('Distance',help='Distance (km) between zip location and the cci.')
                }
res_partner_zip()


class res_partner_job(osv.osv):

    def unlink(self, cr, uid, ids, context={}):
        #Unlink related contact if: no other job AND not self_sufficient
        job_ids=self.pool.get('res.partner.job').browse(cr, uid, ids)
        for job_id in job_ids:
            id_contact = job_id.contact_id.id
            super(res_partner_job,self).unlink(cr, uid, job_id.id,context=context)
            if id_contact:
                data_contact=self.pool.get('res.partner.contact').browse(cr, uid,[id_contact])
                for data in data_contact:
                    if (not data.self_sufficent) and (not data.job_ids):
                        self.pool.get('res.partner.contact').unlink(cr, uid,[data.id], context)
        return True

    def create(self, cr, uid, vals, *args, **kwargs):
        if vals.has_key('function_code_label') and vals['function_code_label']:
            temp = ''
            for letter in vals['function_code_label']:
                res = self.pool.get('res.partner.function').search(cr, uid, [('code','=', letter)])
                if res:
                    temp += self.pool.get('res.partner.function').browse(cr, uid,res)[0].code
            vals['function_code_label'] = temp or vals['function_code_label']
        if 'function_id' in vals and not vals['function_id']:
            vals['function_id'] = self.pool.get('res.partner.function').search(cr, uid, [])[0]
        return super(res_partner_job,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        if vals.has_key('function_code_label') and vals['function_code_label']:
            temp = ''
            for letter in vals['function_code_label']:
                res = self.pool.get('res.partner.function').search(cr, uid, [('code','=', letter)])
                if res:
                    temp += self.pool.get('res.partner.function').browse(cr, uid,res)[0].code
            vals['function_code_label'] = temp or vals['function_code_label']
        if 'function_id' in vals and not vals['function_id']:
            vals['function_id'] = self.pool.get('res.partner.function').search(cr, uid, [])[0]
        return super(res_partner_job,self).write(cr, uid, ids,vals, *args, **kwargs)


    def on_change_phone_num(self, cr, uid, id, phone):
        return check_phone_num(self, cr, uid, id, phone)

    _inherit = 'res.partner.job'
    _columns = {
        'function_label':fields.char('Function Label',size=128),
        'function_code_label':fields.char('Codes',size=128,),
        'date_start':fields.date('Date start'),
        'date_end':fields.date('Date end'),
        'canal_id':fields.many2one('res.partner.canal','Canal',help='favorite chanel for communication'),
        'active':fields.boolean('Active'),
        'who_presence':fields.boolean('In Whos Who'),
        'dir_presence':fields.boolean('In Directory'),
        'department': fields.char('Department',size=20),
    }

    _defaults = {
        'who_presence' : lambda *a: True,
        'dir_presence' : lambda *a: True,
        'active' : lambda *a: True,
    }

res_partner_job()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _description = 'res.partner.address'

    def create(self, cr, uid, vals, *args, **kwargs):
        if vals.has_key('zip_id') and vals['zip_id']:
            vals['zip'] = self.pool.get('res.partner.zip').browse(cr, uid,vals['zip_id']).name
            vals['city'] = self.pool.get('res.partner.zip').browse(cr, uid,vals['zip_id']).city
        return super(res_partner_address,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        if vals.has_key('zip_id') and vals['zip_id']:
            vals['zip'] = self.pool.get('res.partner.zip').browse(cr, uid,vals['zip_id']).name
            vals['city'] = self.pool.get('res.partner.zip').browse(cr, uid,vals['zip_id']).city
        return super(res_partner_address,self).write(cr, uid, ids,vals, *args, **kwargs)


    def get_city(self, cr, uid, id):
        return self.browse(cr, uid, id).zip_id.city
#que faire du name?

#    def _get_name(self, cr, uid, ids, name, arg, context={}):
 #       res={}
  #      for add in self.browse(cr, uid, ids, context):
   #           if add.contact_id:
    #              res[add.id] = (add.department or '') + ' ' + add.contact_id.name
     #         else:
      #            res[add.id] = add.department
       # return res

    def on_change_phone_num(self, cr, uid, id, phone):
        return check_phone_num(self, cr, uid, id, phone)

    _columns = {
        #'name': fields.function(_get_name, method=True, string='Contact Name',type='char',size=64),#override parent field
        'state': fields.selection([('correct','Correct'),('to check','To check')],'Code'),
        'zip_id':fields.many2one('res.partner.zip','Zip'),
        'active': fields.boolean('Active'),
        'sequence_partner':fields.integer('Sequence (Partner)',help='order of importance of this address in the list of addresses of the linked partner'),
        'write_date' : fields.datetime('Last Modification'),
        'write_uid' : fields.many2one('res.users','Last Modifier',help='The last person who has modified this address'),
        'activity_description':fields.text('Local Activity Description',translate=True),
        'local_employee': fields.integer('Nbr of Employee (Site)',help="Nbr of Employee in the site (for the directory)"),
        'dir_show_name' : fields.char('Directory Shown Name', size=128, help="Name of this address printed in the directory of members"),
        'dir_sort_name' : fields.char('Directory Sort Name', size=128, help="Name of this address used to sort the partners in the directory of members"),
        'dir_exclude' : fields.boolean('Directory exclusion', help='Check this box to exclude this address of the directory of members'),
        'notdelivered' : fields.date('Post Return', help='Date of return of mails not delivered at this address'),
    }
    _defaults = {
         'state' : lambda *a: 'correct',
         'active' : lambda *a: 1,
    }

    def onchange_user_id(self, cr, uid, ids,zip_id):
    #Changing the zip code can change the salesman
        if not ids or not zip_id:
            return {}
        id = self.browse(cr, uid, ids)[0]
        if not id.partner_id.user_id:
            data_add=self.pool.get('res.partner.address').browse(cr, uid,ids)
            if zip_id:
                for data in data_add:
                    if data.type=='default':
                        data_zip=self.pool.get('res.partner.zip').browse(cr, uid,[zip_id])
                        for data1 in data_zip:
                             if data1.user_id:
                                 self.pool.get('res.partner').write(cr, uid,[data.partner_id.id],{'user_id':data1.user_id.id})
        return {}

#    def onchange_contact_id(self, cr, uid, ids, contact_id):
#        #return name
#        if not contact_id:
#            return {'value':{'name' : False}}
#        contact_data=self.pool.get('res.partner.contact').browse(cr, uid, contact_id)
#        return {'value':{'name' : contact_data.name}}


res_partner_address()

class res_partner_activity_list(osv.osv):#new object added!
    _name = "res.partner.activity.list"
    _description = 'res.partner.activity.list'
    _columns = {
        'name': fields.char('Code list',size=256,required=True),
        'abbreviation':fields.char('Abbreviation',size=16),
    }
res_partner_activity_list()

class res_partner_activity(osv.osv):#modfiy res.activity.code to res.partner.activity
    _name = "res.partner.activity"
    _description = 'res.partner.activity'
    _rec_name = 'code'
    def name_get(self, cr, uid, ids, context={}):
        #return somethong like”list_id.abbreviation or list_id.name – code”
        res = []
        for act in self.browse(cr, uid, ids, context):
            res.append( (act.id, (act.code or '')+' - '+(act.label or '')))
#        data_activity = self.read(cr, uid, ids, ['list_id','code'], context)
#        res = []
#        list_obj = self.pool.get('res.partner.activity.list')
#        for read in data_activity:
#            if read['list_id']:
#                data=list_obj.read(cr, uid, read['list_id'][0],['abbreviation','name'], context)
#                if data['abbreviation']:
#                    res.append((read['id'], data['abbreviation']))
#                else:
#                    str=data['name']+'-'+read['code']
#                    res.append((read['id'],str))
        return res
    _columns = {
        'code': fields.char('Code',size=6,required=True),
        'label':fields.char('Label',size=250,transtale=True,required=True),
        'description':fields.text('Description'),
        'code_relations':fields.many2many('res.partner.activity','res_activity_code_rel','code_id1','code_id2','Related codes'),
        #'partner_id':fields.many2one('res.partner','Partner'),
        'list_id':fields.many2one('res.partner.activity.list','List',required=True)
    }
res_partner_activity()

class res_partner_map_activity(osv.osv):
    _name = "res.partner.map.activity"
    _description = 'res.partner.map.activity'
    _rec_name = 'activity_id'

    _columns = {
        'activity_pj_id':fields.many2one('res.partner.activity','Activity PJ', ondelete="cascade" ),
        'activity_n_id':fields.many2one('res.partner.activity','Activity N', ondelete="cascade"),
    }
res_partner_map_activity()

class res_partner_activity_relation(osv.osv):
    _name = "res.partner.activity.relation"
    _description = 'res.partner.activity.relation'
    _rec_name = 'activity_id'

    def default_get(self, cr, uid, fields, context={}):
        data = super(res_partner_activity_relation, self).default_get(cr, uid, fields, context)
        if context.get('activities'):
            map_obj = self.pool.get('res.partner.map.activity')
            done = []
            for i in context['activities']:
                if i[2]:
                    if i[2]['activity_id']:
                        print context['activities']
                        activity_id = i[2]['activity_id']
                        activity_ids = map_obj.search(cr, uid, ['|',('activity_pj_id','=',activity_id),('activity_n_id','=',activity_id)])
                        if activity_ids:
                            for activ_item in map_obj.browse(cr, uid, activity_ids):
                                if activ_item.activity_pj_id.id == activity_id and (activ_item.activity_pj_id.id not in done):
                                    data['activity_id'] =  activ_item.activity_n_id.id
                                    done.append(activ_item.activity_n_id.id)
                                elif activ_item.activity_n_id.id == activity_id and (activ_item.activity_n_id.id not in done):
                                    data['activity_id'] =  activ_item.activity_pj_id.id
                                    done.append(activ_item.activity_pj_id.id)
        return data

    _columns = {
        'importance': fields.selection([('main','Main'),('primary','Primary'),('secondary','Secondary')],'Importance',required=True),
        'activity_id':fields.many2one('res.partner.activity','Activity', ondelete="cascade"),
        'partner_id':fields.many2one('res.partner','Partner', ondelete="cascade"),
    }
    _defaults = {
        'importance': lambda *args: 'main'
    }
res_partner_activity_relation()

class res_partner_function(osv.osv):
    _inherit = 'res.partner.function'
    _description = 'Function of the contact inherit'

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context)
        res = []
        str1=''
        for record in reads:
            if record['name'] or record['code']:
                str1=record['name']+'('+(record['code'] or '')+')'
            res.append((record['id'], str1))
        return res
res_partner_function()

class res_partner_relation_type(osv.osv):
    _name = "res.partner.relation.type"
    _description ='res.partner.relation.type'
    _columns = {
        'name': fields.char('Contact',size=50, required=True),
    }
res_partner_relation_type()

class res_partner_relation(osv.osv):
    _name = "res.partner.relation"
    _description = 'res.partner.relation'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one('res.partner','Partner', required=True),
        'current_partner_id':fields.many2one('res.partner','Partner', required=True),
        'description':fields.text('Description'),
        'percent':fields.float('Ownership'),
        'type_id':fields.many2one('res.partner.relation.type','Type', required=True),
    }
res_partner_relation()

class res_partner_country_relation(osv.osv):
    _name = "res.partner.country.relation"
    _description = 'res.partner.country.relation'
    _columns = {
        'frequency': fields.selection([('frequent','Frequent'),('occasional','Occasionnel'),('prospect','Prospection')],'Frequency'),
        'partner_id':fields.many2one('res.partner','Partner'),
        'country_id':fields.many2one('cci.country','Country'),
        'type':fields.selection([('export','Export'),('import','Import'),('saloon','Salon'),('representation','Representation'),('expert','Expert')],'Types'),
    }
res_partner_country_relation()

class res_partner_contact(osv.osv):

    def on_change_phone_num(self, cr, uid, id, phone):
        return check_phone_num(self, cr, uid, id, phone)

    _inherit='res.partner.contact'
    _columns = {
        'article_ids': fields.many2many('res.partner.article','res_partner_contact_article_rel','contact_id','article_id','Articles'),
    }

res_partner_contact()

class res_partner_photo(osv.osv):
    _name='res.partner.photo'
    _order = 'date desc'
    _columns = {
        'partner_chg_ids':fields.one2many('res.partner.change','photo_id','Partner Changes'),
        'address_chg_ids':fields.one2many('res.partner.address.change','photo_id','Address Changes'),
        'partner_new_ids':fields.one2many('res.partner.address.new','photo_id','New Partners'),
        'partner_state_ids':fields.one2many('res.partner.state.register','photo_id','State Changes'),
        'partner_lost_ids':fields.one2many('res.partner.address.lost','photo_id','Losts'),
        'name': fields.char('Photo Name', size=164, select=True),
        'date': fields.date('Date', size=64, select=True),
    }
    _defaults = {
        'name': lambda *a: 'Photo '+time.strftime('%Y-%m-%d'),
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

res_partner_photo()

class res_partner_state_register(osv.osv):

    _name='res.partner.state.register'
    _columns = {
        'name': fields.char('Code', size=64, select=True),
        'old_state': fields.many2one('res.partner.state', 'Old State'),
        'new_state': fields.many2one('res.partner.state', 'New State'),
        'partner_id': fields.many2one('res.partner','Partner Name'),
        'address_id': fields.many2one('res.partner.address','Address'),
        'photo_id':fields.many2one('res.partner.photo','Photo',ondelete="cascade"),
    }
res_partner_state_register()


class res_partner_address_change(osv.osv):

    _name='res.partner.address.change'
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.many2one('res.partner','Partner Name'),
        'old_address': fields.char('Old Address', size=264),
        'new_address': fields.char('New Address', size=264),
        'address_id': fields.many2one('res.partner.address','Address'),
        'photo_id':fields.many2one('res.partner.photo','Photo', ondelete="cascade")
    }

res_partner_address_change()

class res_partner_change(osv.osv):
    _name='res.partner.change'
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('New Name', size=264),
        'old_name': fields.char('Old Name', size=264),
        'address_id': fields.many2one('res.partner.address','Address'),
        'photo_id':fields.many2one('res.partner.photo','Photo', ondelete="cascade")
    }
res_partner_change()


class res_partner_address_new(osv.osv):

    _name='res.partner.address.new'
    _rec_name = 'code'
    _columns = {
        'code': fields.char('Code', size=64),
        'address': fields.char('Postal Address', size=264),
        'state_activity': fields.many2one('res.partner.state', 'State Activity'),
        'name': fields.many2one('res.partner','Partner'),
        'address_id': fields.many2one('res.partner.address','Address'),
        'photo_id':fields.many2one('res.partner.photo','Photo', ondelete="cascade"),
    }
res_partner_address_new()


class res_partner_address_lost(osv.osv):

    _name='res.partner.address.lost'
    _columns = {
        'name': fields.char('Code', size=64),
        'state_activity': fields.many2one('res.partner.state', 'State Activity'),
        'address_id': fields.many2one('res.partner.address','Address'),
        'partner_id': fields.many2one('res.partner','Partner'),
        'photo_id':fields.many2one('res.partner.photo', 'Photo', ondelete="cascade"),
    }

res_partner_address_lost()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


