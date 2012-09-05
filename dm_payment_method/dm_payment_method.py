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
from osv import fields
from osv import osv

class dm_payment_nature(osv.osv):
    _name = 'dm.payment.nature'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
        }
    
dm_payment_nature()

class dm_payment_mode(osv.osv):
    _name = 'dm.payment.mode'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
        'nature_id':fields.many2one('dm.payment.nature', 'Payment Nature'),
        }
    
dm_payment_mode()

class dm_payment_method(osv.osv): # {{{
    _name = 'dm.payment_method'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', domain="[('type','=','cash')]"),
        'logo': fields.binary('Logo'),
        'threshold': fields.float('Amount Threshold (%)', digits=(16, 2)),
        'mode_id': fields.many2one('dm.payment.mode', 'Payment Mode'),

    }
    
dm_payment_method() # }}}

class dm_campaign(osv.osv): #{{{
    _inherit = "dm.campaign"
    _columns = {
         'journal_id': fields.many2one('dm.payment_method', 'Journal'),
    }
    
dm_campaign() #}}}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
