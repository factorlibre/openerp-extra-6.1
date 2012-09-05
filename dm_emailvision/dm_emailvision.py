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

class dm_emailvision_template(osv.osv):#{{{
    _name = "dm.emailvision.template"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=32, required=True),
        'ev_encrypt': fields.char('Emailvision Encrypt Key', size=64),
        'ev_random': fields.char('Emailvision Random Key',size=64),
        }
        
dm_emailvision_template()#}}}

class dm_offer_document(osv.osv):#{{{
    _inherit = "dm.offer.document"
    _columns = {
                
         'ev_template': fields.many2one('dm.emailvision.template', 'Default Emailvision Template'),

    }
dm_offer_document()#}}}

class dm_mail_service(osv.osv):
    _inherit = "dm.mail_service"
    _columns = {
        'ev_host': fields.char('Emailvision Host', size=64),
        'ev_service': fields.char('Emailvision Service', size=64),
        'ev_template': fields.many2one('dm.emailvision.template', 'Emailvision Template'),
    }
    _defaults = {
        'ev_host': lambda *a : 'api.notificationmessaging.com',
        'ev_service': lambda *a : 'NMSXML',
    }
dm_mail_service()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
