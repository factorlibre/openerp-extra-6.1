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
from osv import fields
from osv import osv

class dm_as_reject(osv.osv):#{{{
    _inherit = "dm.as.reject"
    _columns = {
                
       'payment_method_ids': fields.many2many('account.journal', 
                        'reject_payment_method_rel', 'reject_id', 'journal_id',
                        'Payment Methods', domain=[('type','=','cash')]),
    }
dm_as_reject()#}}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
