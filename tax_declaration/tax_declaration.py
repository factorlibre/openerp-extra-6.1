# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
from osv import osv
from osv import fields
from datetime import date
from time import *
import time
import datetime
import string

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'no_of_childrean':fields.selection([
            ('0','None'),        
            ('1','1'),
            ('2','More than 1'),
            
        ],'No. of Childrean', select=True, required=True),
    }
hr_employee()    
    
class account_fiscalyear(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = 'account.fiscalyear'
    _columns = {
        'tax_slab_ids':fields.one2many('hr.tax.slab', 'tax_slab_id', 'Tax Slab', required=False),
        
    }    
account_fiscalyear()

class hr_tax_slab(osv.osv):
    _name = 'hr.tax.slab'
    _description = 'Tax Slab'
    
    _columns = {
        'min_amt': fields.float('Slab From', digits=(16, 2)),
        'max_amt': fields.float('Slab To', digits=(16, 2)),
        'gender':fields.selection([
            ('male','Male'),
            ('female','Female'),
            ('none','None'),
        ],'Gender', select=True),
        'tax_percent': fields.float('Tax Percentage', digits=(16, 2)),    
        'tax_slab_id':fields.many2one('account.fiscalyear', 'Tax Slab', required=False),
            
    }
    _defaults = {
        'gender': lambda *a: 'female',
    }    
hr_tax_slab()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _description = 'Contract'
    _columns = {
        'city_type':fields.selection([
            ('metro','Metro'),
            ('nonmetro','Non-Metro'),
            
        ],'City Type', select=True, readonly=False),
    }
    _defaults = {
        'city_type': lambda *a: 'metro',
    }
hr_contract()
class hr_calculation_type(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.calculation.type'
    _description = 'Open ERP Model'
    
    _columns = {
        'name':fields.char('Operation Name', size=64, required=False, readonly=False),
        'type':fields.selection([
            ('calc','Calculation'),
            ('func','Function'),
            ('user_func','User Defines Function'),#dynamically add the arguments if any:fix later            
            
        ],'Operation Type', select=True),
        
        'operation':fields.char('Operator/Function Name', size=64, required=False, readonly=False),        
    }
hr_calculation_type()
class hr_calculation(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.calculation'
    _description = 'Calculations'
    
    _columns = {
#        'name':fields.char('Calculation Type', size=64, required=False, readonly=False),
#        'calculation_type_id':fields.many2one('hr.calculation.type', 'Calculation Type', required=True),
#        'operand':fields.char('Operand', size=64, required=False, readonly=False),
#        
#        
#        'child_calculation_id':fields.many2one('hr.calculation', 'test', required=False),
#        
#        'child_calculation_ids':fields.one2many('hr.calculation', 'child_calculation_id', 'Child Calculations', required=False),
        
        'type':fields.selection([
            ('func','Function'),
            ('fixed','Fixed Amount'),
            ('formula','Formula'),            
        ],'Calculation Type', select=True),
        
        'function':fields.selection([
            ('min','Minimum'),
            ('max','Maximum'),
        ],'Function', select=True),        
        
        'formula':fields.char('Formula', size=64, required=False, readonly=False),
        'fixed': fields.float('Fixed Amount', digits=(16, 2)),
        
        'child_calculation_id':fields.many2one('hr.calculation', 'test', required=False),
        
        'child_calculation_ids':fields.one2many('hr.calculation', 'child_calculation_id', 'Child Calculations', required=False),
        
        'calculation_id':fields.many2one('hr.allounce.deduction.categoty', 'Payment Category', required=False),
        
        'gender':fields.selection([
            ('male','Male'),
            ('female','Female'),
            ('none','None'),
        ],'Gender', select=True),
        
        'city_type':fields.selection([
            ('metro','Metro'),
            ('nonmetro','Non-Metro'),
            
        ],'City Type', select=True, readonly=False),

        
    }
    _defaults = {
        'type': lambda *a: 'formula',
    }
    
hr_calculation()

class hr_payroll_metro_city(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.payroll.metro.city'
    _description = 'Metro Cities'
    
    _columns = {
        'name':fields.char('Metro City', size=64, required=False, readonly=False),
        
    }
hr_payroll_metro_city()
class payment_category(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = 'hr.allounce.deduction.categoty'
    
    _columns = {    
        'min_capacity': fields.float('Min. Amount', digits=(16, 2)),
        'max_capacity': fields.float('Max. Amount', digits=(16, 2)),
        'defined_by':fields.selection([
            ('govt','Government'),
            ('company','Company'),
            
        ],'Defined By', select=True),   
        'calculation_ids':fields.one2many('hr.calculation', 'calculation_id', 'Calculations', required=False),                   
    }
payment_category()   
 
def M(d): return d.year*12 + d.month

def D(d1,d2): return d1.toordinal() - (d2.toordinal())

def I(mdy): return date(*strptime(mdy, "%Y-%m-%d")[:3])

def month_diff(end_date, start_date): 
    d2=I(end_date)
    d1=I(start_date)+datetime.timedelta(days=-1)
    days = D(d2, d1)
    if days < 0:
        print "Date entered is earlier than today."
     
    months = M(d2) - M(d1)
    if d2.day < d1.day: months -= 1
    tot = date.fromtimestamp(mktime(
        (d1.year, d1.month+months, d1.day+1, 0, 0, 0, 0, 0, 1)))
    return months
    
class tax_declaration(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.tax.declaration'
    _description = 'Tax Declaration Model'
    

    def _calculate_total(self, cr, uid, ids, field_names, arg, context):
        
        contract_wise_argument={}
        employee_allowance = {}
        allowance_objects={}
        allowance_ids={}
        res = {}       
        cur_obj = self.browse(cr, uid, ids, context)[0]
        res[cur_obj.id] = {
#                'total_income': 0.0,
#                'total_investment': 0.0,
        }
        emp_obj = self.pool.get("hr.employee").browse(cr, uid, uid, context=context)        
        
        gender = emp_obj.gender
        no_of_childrean = int(emp_obj.no_of_childrean)
        total_months_of_contract = 0         
        for contract in emp_obj.contract_ids:          
            months_of_contract = month_diff(contract.date_end, contract.date_start)
            total_months_of_contract += months_of_contract

        for allowance in cur_obj.allowance_ids:
            employee_allowance[allowance.allowance_type_ids.code]=allowance.amount/total_months_of_contract
            allowance_ids[string.lower(allowance.allowance_type_ids.code)]=allowance.id

        test_obj = self.pool.get('hr.employee').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0]).name
        
#        query1 = 'select hpl.type, hpl.amount, rpf.name from hr_payslip_line hpl, res_partner_function rpf, hr_employee_grade where hpl.function_id=(select function from hr_contract where employee_id=(select id from hr_employee where user_id='+(str(uid))+')) and rpf.id = hr_employee_grade.function_id'

        #query1= ' select hpl.type, hpl.amount, rpf.name from hr_payslip_line hpl, res_partner_function rpf,     hr_employee_grade,res_users,hr_employee, hr_contract where hr_employee.user_id=res_users.id and hr_employee.id=hr_contract.employee_id and hr_contract.function=hpl.function_id and rpf.id = hr_employee_grade.function_id and res_users.id='+(str(uid))

#        cr.execute(query1)
#        
#        res1 = cr.dictfetchall()
#        print res1
#        
#        print ":-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*:-*"
#        

        salary = 0.0
        final_allowance = 0.0
        final_deduction = 0.0
        basic={}          

        for contract in emp_obj.contract_ids:
            all_arguments={}
            #print contract.name, contract.function.name
            all_arguments['city_type'] = contract.city_type
            months_of_contract = month_diff(contract.date_end, contract.date_start)
            total_months_of_contract += months_of_contract
            all_arguments['month'] = months_of_contract
            wage_type = contract.wage_type_id.type
            monthly_wage=contract.wage
            basic_amount = monthly_wage
            print "basic_amount....", basic_amount
            total_allowance_per_contract = 0.0
            total_deduction_per_contract = 0.0
            all_allowances={}
            for line in contract.function.line_ids:
                allowances={}
                #assumption:allowance will be given yearly
                #NEED TO CHECK WHETHER ALLWANCE DEDUCTION IS DEFINED BY GOVT WHICH MAY BE FIX
                
                monthly_amount = line.amount    
                
                print "line.amount--------",line.amount
                if line.type == 'allounce':
                    if line.category_id.type == 'allow':
                        if wage_type=='gross' or wage_type=='net':
                            #print "allo---",wage_type,"-----", monthly_amount
                            basic_amount -= monthly_amount
                            print "######basic_amount....", basic_amount     
                            
                        if string.lower(line.category_id.code) == 'ce' :
                              monthly_amount =  no_of_childrean * 100
                                              
                        allowance_per_contract = monthly_amount * months_of_contract
                        
                        allowances['company_'+string.lower(line.category_id.code)]=monthly_amount 

                        if line.category_id.code in employee_allowance:
                            allowances['emp_'+string.lower(line.category_id.code)]=employee_allowance[line.category_id.code]       

                        allowance_objects[string.lower(line.category_id.code)]=line.category_id
                        
                        all_allowances[string.lower(line.category_id.code)] = allowances 
                        print "allowance_per_contract---", allowance_per_contract
                        

                        total_allowance_per_contract += allowance_per_contract

                elif line.type == 'deduction':                
                    if line.category_id.type == 'deduct':
                        if wage_type=='net':
                            basic_amount += monthly_amount             

                        deduction_per_contract = monthly_amount * months_of_contract
                        total_deduction_per_contract += deduction_per_contract
                                                        
            all_arguments['basic'] = basic_amount
            all_arguments['no_of_childrean'] = no_of_childrean
            all_arguments['allowances'] = all_allowances
            contract_wise_argument[contract.name]=all_arguments
            salary += (monthly_wage*months_of_contract) 
                       
            final_allowance += total_allowance_per_contract
            final_deduction += total_deduction_per_contract
            #print "all_arguments.......", all_arguments


        print "\ncontract_wise_argument.......", contract_wise_argument
        
        print "\nallowance_objects--->>>",allowance_objects
        
        print "\nemployee_allowance-------->>", employee_allowance
        
        #substract all deductions to find net salary of month
        if wage_type=='gross':
            salary -= final_deduction
        #Add Allowances & substract all deductions to find net salary of month        
        elif wage_type=='basic':  
            salary += final_allowance
            salary -= final_deduction
            
        res[cur_obj.id]['salary']=salary
        
#==============================================================================================================
       #contract_wise_argument
       #allowance_objects
        final=0.0
        obj = None
        final_allowances={}
        
        for contract_name, contract_info in contract_wise_argument.iteritems():
            allowances = contract_info['allowances']    
            city_type = contract_info['city_type'] 
            final_result = 0.0                    
            for allowance_name, allowance_info in allowances.iteritems():
                
                user_amt_key = "emp_"+string.lower(allowance_name)
                if user_amt_key in allowance_info:
                    for calculation in allowance_objects[allowance_name].calculation_ids:
                        if calculation.type == 'func':
                            results=[]
                            
                            query1 = 'select formula from hr_calculation where child_calculation_id='+str(calculation.id)   +' and gender=\''+ gender +'\' and city_type=\''+city_type+'\''
                            
                            cr.execute(query1)
                            res1 = cr.fetchall()
                            
                            for formula_tuple in res1:
                                for formula in formula_tuple:
                                    #print formula, '<<---->>', eval(formula,contract_info,allowance_info)
                                    results.append(str(eval(formula,contract_info,allowance_info)))    
                            
                            #for child_calc in calculation.child_calculation_ids:
                                
                            #print ",".join(results)
                            final_result = eval(calculation.function+'('+",".join(results)+')')
                            print "final_result...",final_result
                        elif calculation.type == 'fixed':
                            print 'Fixed Calculations'
                        elif calculation.type == 'formula':
                            final_result = eval(calculation.formula, contract_info,allowance_info)
                            #print 'Formula calc......', calculation.formula, final_result
                    final_result *= contract_info['month']
                    if allowance_name in final_allowances:
                        final_allowances[allowance_name] += final_result
                    else:
                        final_allowances[allowance_name] = final_result
                    print "final_allowances...", final_allowances    
#                if allowance_name in allowance_ids :  
#                    

#                    final_result += aobj.allowed_amount            
#                    aobj.write( {'allowed_amount':final_result})
        
        total_allowance=0.0
        for allowance_name, final_allowance in final_allowances.iteritems():
            aobj = self.pool.get('hr.tax.declaration.line').browse(cr, uid, allowance_ids[allowance_name], context)            
            aobj.write( {'allowed_amount':final_allowance})
            total_allowance += final_allowance
                                         
        res[cur_obj.id]['total_allowance']=total_allowance
#==============================================================================================================    
        print "###################################################################"
        #print "#########", cur_obj.id
        total_income = 0.0
        for income in cur_obj.income_ids:
                total_income+=income.amount
        res[cur_obj.id]['total_income']=total_income
        total_investment = 0.0
        for investment in cur_obj.investment_ids:
                total_investment+=investment.amount
        res[cur_obj.id]['total_investment']=total_investment
        
#        res[cur_obj.id]={
#            'total_income':total_income,
#            'total_investment':total
#        }
        print res
        print "00000000000000000000000000000000000000000000000000000000000000000000000000"
        taxable_income = salary + total_income - total_investment -total_allowance
        print "Taxable Income---", taxable_income

        query1 = 'select min_amt, max_amt, tax_percent from hr_tax_slab where gender=\''+ gender +'\' order by min_amt desc' 
                            
        cr.execute(query1)
        res1 = cr.dictfetchall()
        print res1        
        
        total_tax = 0.0

        for slab_dict in res1:
            min_amt = slab_dict['min_amt']
            tax_percent = slab_dict['tax_percent']                        
            if taxable_income > min_amt:
                total_tax += (taxable_income-min_amt)*tax_percent                 
                taxable_income = min_amt
                print total_tax, taxable_income
            
        res[cur_obj.id]['tax_to_be_deducted']=total_tax + (total_tax * .03)
        print res
        return res

    _columns = {
        'name':fields.char('Employee Name', size=64, required=False, readonly=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', required=True),
        'company_id':fields.many2one('res.company', 'Company', required=True, readonly=True),
        'salary': fields.function(_calculate_total, method=True, type='float', string='Salary', store=True, readonly=True, multi = 'total'),
        
        
        'income_ids':fields.one2many('hr.tax.declaration.line', 'income_id', 'Incomes', required=False),
        'investment_ids':fields.one2many('hr.tax.declaration.line', 'investment_id', 'Investments', required=False),
        'allowance_ids':fields.one2many('hr.tax.declaration.line', 'allowance_id', 'Allowances', required=False),
        
        'total_income': fields.function(_calculate_total, method=True, type='float', string='Total Income', store=True, readonly=True, multi = 'total'),
        
        'total_investment': fields.function(_calculate_total, method=True, type='float', string='Total Investment', store=True, readonly=True, multi = 'total'),
        'total_allowance': fields.function(_calculate_total, method=True, type='float', string='Total Allowance', store=True, readonly=True, multi = 'total'),
        
        'tax_to_be_deducted':  fields.function(_calculate_total, method=True, type='float', string='Tax Payable', store=True, readonly=True, multi = 'total'),
        
        
        'state':fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            
        ],'State', select=True, readonly=True),    
        
    }
    _defaults = {
        #to bring the company associated with the user according to user login name
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'employee_id': lambda self, cr, uid, context: \
                self.pool.get('hr.employee').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0]).id,
        #employee associated with the user                
        'name': lambda self, cr, uid, context: \
                self.pool.get('hr.employee').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0]).name                
    }    
tax_declaration()

class tax_declaration_line_type(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.tax.declaration.line.type'
    _description = 'Tax Declaration Type Model'
    
    _columns = {
        'name':fields.char('Declaration Type', size=64, required=False, readonly=False),
        'type':fields.selection([
            ('income','Income'),
            ('investment','Investment'),
            
        ],'Type', select=True, required=True),
    }
tax_declaration_line_type()
class tax_declaration_line(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.tax.declaration.line'
    _description = 'Tax Declaration Line Model'
    
    _columns = {
        'name':fields.char('Narration', size=64, required=False, readonly=False),
        'declaration_line_type_id':fields.many2one('hr.tax.declaration.line.type', 'Declaration Type', required=False),
        'allowance_type_ids':fields.many2one('hr.allounce.deduction.categoty', 'Allowance Type', required=False),
        
        #TODO : import time required to get currect date
        'date': fields.date('Date'),
        'amount': fields.float('Amount', digits=(16, 2)),
        'allowed_amount': fields.float('Allowed Allowance', digits=(16, 2), readonly=True),
        
        
        'income_id':fields.many2one('hr.tax.declaration', 'Income', required=False),
        'investment_id':fields.many2one('hr.tax.declaration', 'Investment', required=False),
        'allowance_id':fields.many2one('hr.tax.declaration', 'Allowance', required=False),
    }
tax_declaration_line()

