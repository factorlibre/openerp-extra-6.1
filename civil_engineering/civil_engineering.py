# -*- coding: utf-8 -*-
##############################################################################
#
#    civilengineering module for OpenERP
#    Copyright (C) 2008-2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#       Raimon Esteve <resteve@zikzakmedia.com> All Rights Reserved.
#       Jesús Martín <jmartin@zikzakmedia.com>
#
#    This file is a part of civil_engineering
#
#    civilengineering is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    civilengineering is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time
import xmlrpclib
from tools import config
import decimal_precision as dp


# Civil Engineering Work Class
class civil_engineering_workclass(osv.osv):
    _name = "civil_engineering.workclass"
    _description = "Civil Engineering Work Class"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_workclass where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.workclass', 'Parent Work Class', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.workclass', 'parent_id', 'Child Work Class'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the work class without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_workclass()


# Civil Engineering Work Use
class civil_engineering_workuse(osv.osv):
    _name = "civil_engineering.workuse"
    _description = "Civil Engineering Work Use"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_workuse where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.workuse', 'Parent Work Use', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.workuse', 'parent_id', 'Child Work Use'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the Work Use without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_workuse()


# Civil Engineering Structure Type
class civil_engineering_structuretype(osv.osv):
    _name = "civil_engineering.structuretype"
    _description = "Civil Engineering Structure Type"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_structuretype where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.structuretype', 'Parent Structure Type', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.structuretype', 'parent_id', 'Child Structure Type'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the Structure Type without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_structuretype()


# Civil Engineering Foundation Type
class civil_engineering_foundationtype(osv.osv):
    _name = "civil_engineering.foundationtype"
    _description = "Civil Engineering Foundation Type"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_foundationtype where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.foundationtype', 'Parent Foundation Type', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.foundationtype', 'parent_id', 'Child Foundation Type'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the Foundation Type without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_foundationtype()


# Civil Engineering Structural Model Abstraction
class civil_engineering_modelabstraction(osv.osv):
    _name = "civil_engineering.modelabstraction"
    _description = "Civil Engineering Model Structural"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_modelabstraction where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.modelabstraction', 'Parent Structural Model Abstraction', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.modelabstraction', 'parent_id', 'Child Structural Model Abstraction'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the Structural Model Abstraction without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_modelabstraction()


# Civil Engineering Modeling Software
class civil_engineering_modelingsoftware(osv.osv):
    _name = "civil_engineering.modelingsoftware"
    _description = "Civil Engineering Modeling Software"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from civil_engineering_modelingsoftware where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name':fields.char('Name', size=64),
        'parent_id': fields.many2one('civil_engineering.modelingsoftware', 'Parent Modeling Software', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Full Name'),
        'child_ids': fields.one2many('civil_engineering.modelingsoftware', 'parent_id', 'Child Modeling Software'),
        'active' : fields.boolean('Active', help="The active field allows you to hide the Modeling Software without removing it."),
    }
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive records.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'

civil_engineering_modelingsoftware()


# Civil Engineering Area
class civil_engineering_area(osv.osv):
    _name = "civil_engineering.area"
    _description = "Civil Engineering Area"

    _columns = {
        'name':fields.char('Name', size=64, select=1, required=True),
    }
civil_engineering_area()


# Civil Engineering Work
class civil_engineering_work(osv.osv):
    _name = "civil_engineering.work"
    _description = "Civil Engineering Work"

    _columns = {
        'name':fields.char('Work description', size=128, select=1, required=True),
        'workclass_id':fields.many2one('civil_engineering.workclass','Work Class', select=1, required=True),
        'location':fields.char('Location', size=64),
        'city':fields.char('City', size=64, select=1),
        'main_city':fields.char('Main city', size=64, select=1),
        'country_id':fields.many2one('res.country','Country', select=1),
        'state_id':fields.many2one('res.country.state','State',domain="[('country_id','=',country_id)]"),
        'workuse_id':fields.many2one('civil_engineering.workuse','Work Use', select=1, required=True),
        'constructed_area':fields.float('Constructed area', digits=(12,2), select=2),
        'floors_under_ground_level':fields.integer('Floors under ground level'),
        'floors_above_ground_level':fields.integer('Floors above ground level'),
#        'work_construction_cost':fields.float('Work construction cost', digits=(12, int(config['price_accuracy'])), select=2),
        'work_construction_cost':fields.float('Work construction cost', digits_compute=dp.get_precision('Account'), select=2),
        'structuretype_id':fields.many2one('civil_engineering.structuretype','Structure Type'),
        'foundationtype_id':fields.many2one('civil_engineering.foundationtype','Foundation Type'),
        'modelabstraction_id':fields.many2one('civil_engineering.modelabstraction','Structural Model Abstraction'),
        'distance_between_supports':fields.float('Distance between supports', digits=(12,2)),
        'modelingsoftware_id':fields.many2one('civil_engineering.modelingsoftware','Structure Modeling Software'),
#        'structure_construction_cost':fields.float('Structure construction cost', digits=(12, int(config['price_accuracy']))),
        'structure_construction_cost':fields.float('Structure construction cost', digits_compute=dp.get_precision('Account')),
        'work_owner':fields.many2one('res.partner', 'Work owner', select=2),
        'work_builder':fields.many2one('res.partner', 'Work builder', select=2),
        'architecture':fields.many2one('res.partner', 'Architecture', select=2),
        'civil_engineer':fields.many2one('res.partner', 'Civil engineer', select=2),
        'work_safety':fields.many2one('res.partner', 'Work safety', select=2),
        'project_manager':fields.many2one('res.partner', 'Project manager', select=2),
        'structural_engineering':fields.many2one('res.partner', 'Structural engineering', select=2),
        'plant_engineering':fields.many2one('res.partner', 'Plant engineering', select=2),
        'geotechnics':fields.many2one('res.partner', 'Geotechnics', select=2),
        'project_ids':fields.one2many('civil_engineering.work.project', 'work_id', 'Project'),
    }
    
    def _default_workclass(self, cr, uid, context={}):
        if 'workclass_id' in context and context['workclass_id']:
            return context['workclass_id']
        return []

    def _default_workuse(self, cr, uid, context={}):
        if 'workuse_id' in context and context['workuse_id']:
            return context['workuse_id']
        return []

    def _default_structuretype(self, cr, uid, context={}):
        if 'structuretype_id' in context and context['structuretype_id']:
            return context['structuretype_id']
        return []

    def _default_foundationtype(self, cr, uid, context={}):
        if 'foundationtype_id' in context and context['foundationtype_id']:
            return context['foundationtype_id']
        return []

    def _default_modelabstraction(self, cr, uid, context={}):
        if 'modelabstraction_id' in context and context['modelabstraction_id']:
            return context['modelabstraction_id']
        return []

    def _default_modelingsoftware(self, cr, uid, context={}):
        if 'modelingsoftware_id' in context and context['modelingsoftware_id']:
            return context['modelingsoftware_id']
        return []

    _defaults = {
        'workclass_id': _default_workclass,
        'workuse_id': _default_workuse,
        'structuretype_id': _default_structuretype,
        'foundationtype_id': _default_foundationtype,
        'modelabstraction_id': _default_modelabstraction,
        'modelingsoftware_id': _default_modelingsoftware,
    }
civil_engineering_work()


# Civil Engineering Work Project
class civil_engineering_work_project(osv.osv):
    _name = "civil_engineering.work.project"
    _description = "Civil Engineering Work Project"

    _columns = {
        'work_id':fields.many2one('civil_engineering.work', 'Work', select=True, required=True),
        'sequence':fields.integer('Sequence'),
        'area_id':fields.many2one('civil_engineering.area', 'Area', select=True, required=True),
        'project_id':fields.many2one('project.project', 'Project', select=True, required=True),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for obj in self.browse(cr, uid, ids):
            res.append((obj.id, obj.work_id.name+'-'+obj.area_id.name+'-'+obj.project_id.name))
        return res

civil_engineering_work_project()

