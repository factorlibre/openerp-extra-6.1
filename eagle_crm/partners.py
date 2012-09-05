# -*- coding: utf-8 -*-
#
#  File: partner.py
#  Module: eagle_crm
#
#  Created by sbe@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

from osv import osv,fields

class res_partner(osv.osv):
    """ Inherits partner and adds CRM information in the partner form """
    _inherit = 'res.partner'
    _columns = {
        'opportunity': fields.one2many('crm.lead', 'partner_id', 'Opportunities', domain=[('type','=','opportunity')]),
        'lead': fields.one2many('crm.lead', 'partner_id', 'Leads', domain=[('type','=','lead')] ),
		'offres': fields.one2many('crm.lead', 'partner_id', 'Offres', domain=[('type','=','opportunity'),('state','=','open')] ),
		'claims': fields.one2many('crm.claim', 'partner_id', 'Claims'),
    }
res_partner()
