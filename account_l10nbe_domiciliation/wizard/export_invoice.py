# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import pooler
import wizard
import base64
from osv import osv
import time
from tools.translate import _

form = """<?xml version="1.0"?>
<form string="Export Invoices">
<separator string="Export invoice to DOM80 format" colspan="4" />
   <field name="ref_file" colspan="4" />
   <field name="collection_date" colspan="4" />
   <field name="account_bank_number" colspan="4" />
   <field name="sender" colspan="4" />
   <field name="credit_note" colspan="4" />
</form>"""

fields = {
        'ref_file' : {
        'string':'Reference of the file', 
        'type':'char', 
        'size' : 10,
        'help' : "Reference of the file, Used for Dom80 header",
        'required': True,
    },
    'collection_date' : {
        'string':'Collection Date', 
        'type':'date', 
        'required': True,
        'default' : time.strftime('%Y-%m-%d'),
        'help' : "Requested collection date"
    },
        'sender': {
        'string': 'Document Sender',
        'type': 'many2one',
        'relation': 'res.partner',
        'help': 'This field have to be filled in cases where the sender is different from the creditor'
    },
        'account_bank_number': {
        'string': 'Account Bank Number',
        'type': 'many2one',
        'relation': 'res.partner.bank',
        'help': 'Select here the creditor account number',
        'domain': "[('state','=','bank'),('partner_id','=',1)]", #to improve: partner of the company of the uid
        'required': True
    },
        'credit_note': {
        'string': 'With Credit Note?',
        'type': 'boolean',
        'help': 'Check if you want to export credit note'
    },

    }

save_form = """<?xml version="1.0"?>
<form string="Save File...">
   <field name="invoice_file"/>
   <separator string="Note" colspan="4" />
   <field name="note" colspan="4" nolabel="1" readonly="1"/>
   </form>"""

save_fields = {
    'invoice_file' : {
        'string':'Export File', 
        'type':'binary', 
        'required': False, 
        'readonly':True, 
    }, 
    'note' : {'string':'Log', 'type':'text'}, 
}

trans=[(u'ￃﾩ', 'e'), 
       (u'ￃﾨ', 'e'), 
       (u'ￃﾠ', 'a'), 
       (u'ￃﾪ', 'e'), 
       (u'ￃﾮ', 'i'), 
       (u'ￃﾯ', 'i'), 
       (u'ￃﾢ', 'a'), 
       (u'ￃﾤ', 'a')]

def tr(s):
    s= s.decode('utf-8')
    for k in trans:
        s = s.replace(k[0], k[1])
    try:
        res= s.encode('ascii', 'replace')
    except:
        res = s
    return res

class record:
    def __init__(self, global_context_dict):

        for i in global_context_dict:
            global_context_dict[i]= global_context_dict[i] and tr(global_context_dict[i])
        self.fields = []
        self.global_values = global_context_dict
        self.pre={'padding':'', 'seg_num1':'0', 'seg_num2':'1', 
                  'seg_num3':'1', 'seg_num4':'1', 'seg_num5':'1', 'seg_num8':'1', 'seg_num_t':'9', 
                   'flag':'0', 'flag1':'\n'
                           }
        self.init_local_context()

    def init_local_context(self):
        """
        Must instanciate a fields list, field = (name,size)
        and update a local_values dict.
        """
        raise "not implemented"

    def generate(self):
        res=''
        value=0
        go=True
        for field in self.fields :
            if self.pre.has_key(field[0]):
                value = self.pre[field[0]]
            elif self.global_values.has_key(field[0]):
                value = self.global_values[field[0]]
            else :
                continue
                #raise Exception(field[0]+' not found !')
            try:
                res = res + c_ljust(value, field[1])
            except :
                pass

        return res

class record_header(record):
    def init_local_context(self):
        self.fields=[
            #Header record start
            ('identification', 1), 
            ('zeros', 4), ('creation_date', 6), 
            ('institution_code', 3), ('app_code', 2), ('ref_file', 10), ('id_sender', 11), ('id_creditor', 11), 
            ('acc_num_creditor', 12), ('version_code', 1), ('if_duplicate', 1), ('collection_date', 6), ('blanks', 60)
            ]

class record_trailer(record):
    def init_local_context(self):
        self.fields=[
            #Trailer record start
            ('identification', 1), 
            ('tot_collection', 4), ('tot_amount_collection', 12) , 
             ('tot_collection_direct_debit_num', 15), 
            ('tot_reversal_inst', 4), ('tot_amount_reversal_inst', 12), 
             ('tot_reversal_direct_debit_num', 15), 
            ('blanks', 65), 
            ]

class record_invoice_data(record):
    def init_local_context(self):
        self.fields=[
            ('identification', 1), ('serial_num', 4), ('direct_debit_num', 12), 
            ('type_code', 1), 
            ('amount_collection', 12), ('creditor', 26), ('msg_payer_1', 15), 
            ('msg_payer_2', 15), ('creditor_ref', 12), ('blanks', 30), 
            ]

def c_ljust(s, size):
    """
    check before calling ljust
    """
    s= s or ''
    if len(s) > size:
        s= s[:size]
    s = s.decode('utf-8').encode('latin1', 'replace').ljust(size)
    return s

class Log:
    def __init__(self):
        self.content= ""
        self.error= False
    def add(self, s, error=True):
        self.content= self.content + s
        if error:
            self.error= error
    def __call__(self):
        return self.content

def _create_file(self, cr, uid, data, context):
    v1 = {}
    v2 = {}
    v3 = {}
    log=''
    log = Log()
    blank_space = ' '

    seq = 0
    inv_seq = 0
    total = 0
    inv_total = 0
    invoice_data = ''
    
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    bank_obj = pool.get('res.partner.bank')
    invoice_obj = pool.get('account.invoice')
    obj_cmpny = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid).company_id
    
    #Header Record Start
    
    v1['identification']='0'   #1
    v1['zeros']='0000'  # 2-5
    v1['creation_date']= time.strftime('%d%m%y')    #6-11
    code =  bank_obj.browse(cr, uid, data['form']['account_bank_number']).institution_code
    if not code:
        return {'note':_('Please provide Institution Code number for the bank of the creditor.'), 'invoice_file': False, 'state':'' }
    
    v1['institution_code'] = code # 12-14
    v1['app_code']= '02' # 15-16
    v1['ref_file']= data['form']['ref_file'] or '' # 17-26

    id_creditor = obj_cmpny.partner_id.vat
    if not id_creditor:
        return {'note': _('Please Provide VAT number for the creditor.'), 'invoice_file': False, 'state':'failed' }
    v1['id_creditor']= '0' + id_creditor[-10:]

    sender_rec = data['form']['sender'] and partner_obj.browse(cr, uid, data['form']['sender']) or obj_cmpny.partner_id
    id_sender = sender_rec.vat
    if not id_sender:
        return {'note': _('Please Provide VAT number for the Sender.'), 'invoice_file': False, 'state':'failed' }
    v1['id_sender']= '0' + id_sender[-10:] # 27-37

    #Taken bank account num of main company
    partner_bank = bank_obj.browse(cr, uid, data['form']['account_bank_number']).acc_number
    
    if partner_bank:
        v1['acc_num_creditor'] = partner_bank
    else:
        return {'note':_('Please Provide Bank number for the creditor.'), 'invoice_file': False, 'state':'failed' }
    
    v1['version_code']='5' #61
    v1['if_duplicate']=' ' # 62
    collection_date = time.strptime(data['form']['collection_date'], '%Y-%m-%d')
    v1['collection_date'] = time.strftime('%d%m%y', collection_date)
    v1['blanks'] = ' '*60
    file_header =record_header(v1).generate()
    #Header Record End
    
    #Data Record Start
    direct_debit_num_tot = 0
    inv_direct_debit_num_tot = 0
    if data['form']['credit_note']:
        cr.execute("select id from account_invoice where domiciled=True and domiciled_send_date is null and type in('out_refund', 'out_invoice') and state ='open'")
    else:
        cr.execute("select id from account_invoice where domiciled=True and domiciled_send_date is null and type in('out_invoice') and state ='open'")

    inv_ids = map(lambda x:x[0], cr.fetchall())
    if not inv_ids:
        return {'note': _('There is no no invoices to export'), 'invoice_file': False, 'state':'failed' }
   
    collected_invoice_ids = []
    for inv in invoice_obj.browse(cr, uid, inv_ids):
        seq=seq+1
        v2['identification'] = '1'
        v2['serial_num'] = str(seq)[-4:].rjust(4, '0')
        v2['direct_debit_num'] =  inv.partner_id.domiciliation
        v2['amount_collection'] = (('%.2f' % inv.residual).replace('.', '')).rjust(12, '0')
        v2['msg_payer_1'] = inv.name
        v2['msg_payer_2'] = ''
        v2['creditor_ref' ] = '0' * 12
        v2['blanks' ] = ' ' * 30
        
        if inv.type == 'out_refund':
            v2['type_code'] =  '1'
            inv_total += inv.residual
            inv_seq += 1
            inv_direct_debit_num_tot += int(v2['direct_debit_num'])
            v2['creditor'] = inv.partner_id.name
        else:
            total += inv.residual
            direct_debit_num_tot += int(v2['direct_debit_num'])
            v2['type_code'] =  '0'
            v2['creditor'] = obj_cmpny.partner_id.name#inv.partner_id.name#.ljust(26 , ' ')

        invoice_data = invoice_data+ '\n' + record_invoice_data(v2).generate()
        collected_invoice_ids.append(inv.id)
    #Data Record End
    
    #Trailer Record Start
    v3['identification'] = '9'
    v3['tot_collection'] = str(seq-inv_seq).rjust(4, '0')
    v3['tot_amount_collection'] = (('%.2f' % total).replace('.', '')).rjust(12, '0')
    v3['tot_collection_direct_debit_num'] = str(direct_debit_num_tot).rjust(15, '0')
    
    v3['tot_reversal_inst'] = str(inv_seq).rjust(4, '0')
    v3['tot_amount_reversal_inst']  = (('%.2f' % inv_total).replace('.','')).rjust(12, '0')
    v3['tot_reversal_direct_debit_num']  = str(inv_direct_debit_num_tot).rjust(15, '0')
    
    v3['blanks' ] = ' ' * 65

    file_trailer = '\n' + record_trailer(v3).generate()
    
    #Trailer Record End

    dom_data = file_header + invoice_data + file_trailer
    log.add("Successfully Exported\n--------------------\nSummary:\n\nTotal amount collected : %.2f \nTotal Number of collection : %d \n-------------------- " %(total, seq))
    invoice_obj.write(cr, uid, collected_invoice_ids,{'domiciled_send_date': time.strftime('%Y-%m-%d')},context=context)
    return {'note':log(), 'invoice_file': base64.encodestring(dom_data), 'state':'succeeded', 'inv_ids':collected_invoice_ids}


def float2str(lst):
    return str(lst).rjust(16).replace('.', '')

def _log_create(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    pool.get('invoice.export.log').create(cr, uid, {
        'note': data['form']['note'], 
        'file': data['form']['invoice_file'] and data['form']['invoice_file'] or False, 
        'state': data['form']['state'], 
    })

    return {}

def _check(self, cr, uid, data, context):
    if data['form']['state'] == 'failed':
        return 'failed'
    return 'close'

class wizard_pay_create(wizard.interface):
    
    states = {
        'init' : {
            'actions' : [],  
            'result' : {'type' : 'form', 
                        'arch' : form, 
                        'fields' : fields, 
                        'state' : [('end', 'Cancel'), ('export', 'Export') ]}
        }, 
        'export' : {
            'actions' : [_create_file], 
            'result' : {'type' : 'form', 
                        'arch' : save_form, 
                        'fields' : save_fields, 
                        'state' : [('next_state_check', 'Ok', 'gtk-ok') ]}
        },
       'next_state_check': {
            'actions': [_log_create],
            'result' : {'type': 'choice', 'next_state': _check }
        },
      'failed': {
                'actions': [],
                'result': {'type': 'state', 'state':'end'}
            },

      'close': {
                'actions': [],
                'result': {'type': 'state', 'state':'report'}
            },
      'report': {
            'actions': [],
            'result': {'type':'print', 'report':'invoice.domiciliation.dom', 'state':'end'}
        }
    }
wizard_pay_create('invoice.export.dom')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


