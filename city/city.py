#!/usr/bin/env python
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

from osv import osv, fields
import wizard
import pooler

class city(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for line in self.browse(cr, uid, ids):
            state = line.state_id.name
            country = line.state_id.country_id.name
            location = "%s %s, %s, %s" %(line.zipcode, line.name, state, country)
            res.append((line['id'], location))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('zipcode', 'ilike', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    _name = 'city.city'
    _description = 'City'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', required=True, select=1),
        'name': fields.char('City', size=64, required=True, select=1),
        'zipcode': fields.char('ZIP', size=64, required=True, select=1),
    }
city()


class CountryState(osv.osv):
    _inherit = 'res.country.state'
    _columns = {
        'city_ids': fields.one2many('city.city', 'state_id', 'Cities'),
    }
CountryState()


class res_partner_address(osv.osv):
    _inherit = "res.partner.address"

    def _get_zip(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = obj.location.zipcode
            else:
                res[obj.id] = ""
        return res

    def _zip_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('city.city').search(cr, uid, [('zipcode',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args

    def _get_city(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = obj.location.name
            else:
                res[obj.id] = ""
        return res

    def _city_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('city.city').search(cr, uid, [('name',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args

    def _get_state(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.state_id.id, obj.location.state_id.name]
            else:
                res[obj.id] = False
        return res

    def _state_id_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('city.city').search(cr, uid, [('state_id',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args

    def _get_country(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.state_id.country_id.id, obj.location.state_id.country_id.name]
            else:
                res[obj.id] = False
        return res

    def _country_id_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.country.state').search(cr, uid, [('country_id',operator,value)], context=context)
            address_ids = []
            for country in self.pool.get('res.country.state').browse(cr, uid, ids, context):
                ids += [city.id for city in country.city_ids]
            new_args.append( ('location','in',tuple(ids)) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args

    _columns = {
        'location': fields.many2one('city.city', 'Location'),
        'zip': fields.function(_get_zip, fnct_search=_zip_search, method=True, type="char", string='Zip', size=24),
        'city': fields.function(_get_city, fnct_search=_city_search, method=True, type="char", string='City', size=128),
        'state_id': fields.function(_get_state, fnct_search=_state_id_search, obj="res.country.state", method=True, type="many2one", string='State'),
        'country_id': fields.function(_get_country, fnct_search=_country_id_search, obj="res.country" ,method=True, type="many2one", string='Country'),
    }
res_partner_address()






