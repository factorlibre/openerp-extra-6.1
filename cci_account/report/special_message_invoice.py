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
import time
import datetime
from report import report_sxw
import pooler
from tools import amount_to_text_fr
from tools.amount_to_text_en import amount_to_text as amount_to_text_en
from decimal import Decimal
from tools.translate import translate as _

class account_invoice_with_message(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_with_message, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'spcl_msg': self.spcl_msg,
            'invoice_lines': self.invoice_lines,
            'find_vcs' : self.find_vcs,
            #'fr_convert': self.fr_convert,
            #'en_convert': self.en_convert,
            #'get_value':self._get_value,
            #'get_decimal_value':self._get_decimal_value,
            'get_bic': self._get_bic,
            'get_bank_account': self._get_bank_account,
        })
        self.context = context

    def _get_bank_account(self, invoice_id):
        item = pooler.get_pool(self.cr.dbname).get('account.invoice').browse(self.cr,self.uid,invoice_id)
        s = ''
        if item.partner_bank:
            bank_account = item.partner_bank.state == 'iban' and item.partner_bank.iban or item.partner_bank.acc_number
            #s = ' '.join(map(lambda i : i , bank_account))
            s = bank_account
        return s

    def _get_bic(self, invoice_id):
        item = pooler.get_pool(self.cr.dbname).get('account.invoice').browse(self.cr,self.uid,invoice_id)
        s = ''
        if item.partner_bank:
            if item.partner_bank.bank:
                #s = ' '.join(map(lambda i : i , item.partner_bank.bank.bic))
                s =  item.partner_bank.bank.bic
        return s

    def find_vcs(self,invoice_id):
        item = pooler.get_pool(self.cr.dbname).get('account.invoice').browse(self.cr,self.uid,invoice_id)
        return item.name

    def fr_convert(self, amount):
        amount = Decimal("%f" % (amount, ))
        return amount_to_text_fr(amount, 'euro')

    def en_convert(self, amount):
        amount = Decimal("%f" % (amount, ))
        return amount_to_text_en(amount)

    def _get_value(self,amount):
        x = str(amount)
        x=x.split('.')
        t = str(x[0])
        cir= ''.join(map(lambda i : i , t))
        return cir

    def _get_decimal_value(self,amount):
        x = str(amount)
        x=x.split('.')
        t = len(x) == 2 and str(x[1]) or '00'
        cir= '   '.join(map(lambda i : i , t))
        return cir

    def spcl_msg(self, form):
        if form['message']:
            account_msg_data = pooler.get_pool(self.cr.dbname).get('notify.message').browse(self.cr, self.uid, form['message'])
            msg = account_msg_data.msg
        else:
            msg = ""
        return msg
    def invoice_lines(self,invoice):
        result =[]
        sub_total={}
        info=[]
        invoice_list=[]
        res={}
        list_in_seq={}
        k=0
        ids = self.pool.get('account.invoice.line').search(self.cr, self.uid, [('invoice_id', '=', invoice.id)])
        ids.sort()
        for id in range(0,len(ids)):
            info = self.pool.get('account.invoice.line').browse(self.cr, self.uid,ids[id], self.context.copy())
            list_in_seq[info]=info.sequence
        i=1
        j=0
        final=sorted(list_in_seq.items(), lambda x, y: cmp(x[1], y[1]))
        invoice_list=[x[0] for x in final]
        sum_flag={}
        sum_flag[j]=-1
        for entry in invoice_list:
            k+=1
            is_empty = False
            res={}

            if entry.state=='article':
                self.cr.execute('select tax_id from account_invoice_line_tax where invoice_line_id=%s', (entry.id,))
                tax_ids=self.cr.fetchall()

                if tax_ids==[]:
                    res['tax_types']=''
                else:
                    tax_names_dict={}
                    for item in range(0,len(tax_ids))    :
                        self.cr.execute('select name from account_tax where id=%s', (tax_ids[item][0],))
                        type=self.cr.fetchone()
                        tax_names_dict[item] =type[0]
                    tax_names = ','.join([tax_names_dict[x] for x in range(0,len(tax_names_dict))])
                    res['tax_types']=tax_names
                res['name']=entry.name
                res['quantity']="%.2f"%(entry.quantity)
                res['price_unit']="%.2f"%(entry.price_unit)
                res['discount']="%.2f"%(entry.discount)
                res['price_subtotal']="%.2f"%(entry.price_subtotal)
                sub_total[i]=entry.price_subtotal
                i=i+1
                res['note']=entry.note
                res['currency']=invoice.currency_id.code
                res['type']=entry.state

                if entry.uos_id.id==False:
                    res['uos']=''
                else:
                    uos_name = self.pool.get('product.uom').read(self.cr,self.uid,entry.uos_id.id,['name'],self.context.copy())
                    res['uos']=uos_name['name']
            else:
                res['quantity']=''
                res['price_unit']=''
                res['discount']=''
                res['tax_types']=''
                res['type']=entry.state
                res['note']=entry.note
                res['uos']=''

                if entry.state=='subtotal':
                    res['name']='Sous-Total'
                    sum=0
                    sum_id=0
                    if sum_flag[j]==-1:
                        temp=1
                    else:
                        temp=sum_flag[j]

                    for sum_id in range(temp,len(sub_total)+1):
                        sum+=sub_total[sum_id]
                    sum_flag[j+1]= sum_id +1

                    j=j+1
                    res['price_subtotal']="%.2f"%(sum)
                    res['currency']=invoice.currency_id.code
                    res['quantity']=''
                    res['price_unit']=''
                    res['discount']=''
                    res['tax_types']=''
                    res['uos']=''
                elif entry.state=='title':
                    try:
                        date_title = datetime.datetime.strptime(entry.name.split(' ')[0], "%Y-%m-%d")
                        res['name'] = date_title.strftime('%d-%m-%Y')
                    except:
                        res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=''
                elif entry.state=='text':
                    if not entry.name:
                        is_empty = True
                        res={}
                    else:
                        res['name']=entry.name
                        res['price_subtotal']=''
                        res['currency']=''
                elif entry.state=='line':
                    res = {}
                elif entry.state=='break':
                    res['type']=entry.state
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=''
                else:
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=invoice.currency_id.code

            if not is_empty:
                res['k'] = k
                result.append(res)

        return result

report_sxw.report_sxw('report.cci_account.invoice', 'account.invoice', 'addons/cci_account/report/special_message_invoice.rml', parser=account_invoice_with_message,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

