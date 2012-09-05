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
import time

class dm_as_reject_type(osv.osv):#{{{
    _name = "dm.as.reject.type"
    
    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'code': fields.char('Code', size=32, required=True),
    }
    
dm_as_reject_type()#}}}

class dm_as_reject(osv.osv):#{{{
    _name = "dm.as.reject"
    
    _columns = {
        'name': fields.char('Description', size=128, required=True),
        'type_od': fields.many2one('dm.as.reject.type', 'Type', required=True),
        'reject_type': fields.char('Type', size=64),
        'to_disable': fields.boolean('To Disable')
    }
    
    def on_change_reject_type(self, cr, uid, ids, type_od):
        res = {'value': {}}
        if type_od:
            reject_type = self.pool.get('dm.as.reject.type').read(cr, uid, [type_od])[0]
            res['value'] = {'reject_type': reject_type['code']}
        return res
    
dm_as_reject() #}}}

class dm_address_segmentation(osv.osv): # {{{
    _name = "dm.address.segmentation"
    _description = "Segmentation"
    _inherit = "dm.address.segmentation"
    
    _columns = {
        'ignore_rejects': fields.boolean('Ignore Rejects'),
        'active_only': fields.boolean('Active Only'),
        }
    
    _defaults = {
        'ignore_rejects': lambda *a: 1,
        'active_only': lambda *a: 1,
        }
    
    def set_address_criteria(self, cr, uid, ids, context={}):
        sql_query = super(dm_address_segmentation,self).set_address_criteria(cr, uid, ids, context)
        if type(ids) != type([]):
            ids = [ids]
        if self.browse(cr, uid, ids)[0].active_only:
            if sql_query.find('where') >= 0:
                sql_query = sql_query + ' and pa.active = True'
            else:
                sql_query = sql_query + 'where pa.active = True'
        return sql_query
        
dm_address_segmentation() # }}}

class dm_as_reject_incident(osv.osv): # {{{
    _name = "dm.as.reject.incident"
    _description = "Reject Incidents"
    
    _columns = {
        'date': fields.datetime('Date', required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'partner_address_id': fields.many2one('res.partner.address', 'Partner Address'),
        'reject_id': fields.many2one('dm.as.reject', 'Reject', required=True),
        'origin': fields.char('Origin', size=64),
        'note': fields.text('Description'),
        'active': fields.boolean('Active'),
        }
    _defaults = {
        'active': lambda *a: 1,         
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
        }
dm_as_reject_incident() # }}}

class res_partner(osv.osv): # {{{
    _inherit = "res.partner"
    
    _columns = {
        'reject_ids': fields.one2many('dm.as.reject.incident', 'partner_id', 'Rejects')      
        }
    """
    def write(self, cr, uid, ids, vals, context):
        result = super(res_partner, self).write(cr, uid, ids, vals, context)
        rej_inc_ids = self.browse(cr, uid, ids)[0].reject_ids
        for rej_inc_id in rej_inc_ids:
            for reject_id in rej_inc_id.reject_ids:
                if reject_id.to_disable:
                    cr.execute("update res_partner set active=False where id = %s" %(ids[0]))
                    cr.commit()
                    address_ids = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', ids[0])])
                    for add_id in address_ids:
                        self.pool.get('res.partner.address').write(cr, uid, [add_id], {'active': False}, context)
        return result
    """
res_partner() # }}}

class res_partner_address(osv.osv): # {{{
    _inherit = "res.partner.address"
    
    _columns = {
        'reject_ids': fields.one2many('dm.as.reject.incident', 'partner_address_id', 'Rejects')      
        }
    """    
    def write(self, cr, uid, ids, vals, context):
        for r_id in ids :
            if 'reject_ids' in vals :
                reject_ids = map(lambda x : x[2]['reject_id'],vals['reject_ids'])
                rej_obj = self.pool.get('dm.as.reject').browse(cr,uid,reject_ids)
            else:
                rej_obj= map(lambda x: x.reject_id ,self.browse(cr, uid, r_id).reject_ids)
            for rej_inc_id in rej_obj:
                if rej_inc_id.to_disable:
                    vals['active']=False
        result = super(res_partner_address, self).write(cr, uid, ids, vals, context)
        return result
    """
res_partner_address() # }}}

REJECT_CRITERIAS = [ # {{{
            ('buyer','Product Buyer'),
            ('moved','Moved'),
            ('pay_incident','Payment Incident'),
            ('carrier','Carrier Reject')
            ] # }}}

class dm_campaign_proposition_segment(osv.osv):
    _inherit = "dm.campaign.proposition.segment"
    
    _columns = {
        'reject_criteria' : fields.selection(REJECT_CRITERIAS, 'Reject Criteria'),
                }
    
dm_campaign_proposition_segment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
