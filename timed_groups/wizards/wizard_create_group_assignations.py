# -*- coding: utf-8 -*-
##############################################################################
#
#    school module for OpenERP
#    Copyright (C) 2010 Tecnoba S.L. (http://www.tecnoba.com)
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
#    Copyright (C) 2011 Zikzakmedia S.L. (http://www.zikzakmedia.com)
#       Jesús Martín Jiménez <jmargin@zikzakmedia.com> All Rights Reserved.
#
#    This file is a part of school module
#
#    school OpenERP module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    school OpenERP module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields


class groups_group_assignation_wizard(osv.osv_memory):
    _name = 'groups.group_assignation_wizard'
    
    def _domain_participation(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for obj in self.browse(cr, uid, ids):
            ret[obj.id]=self._default_domain_participation(cr, uid, {'active_id': obj.id})
        return ret

    _columns = {
        'group_id' : fields.many2one('groups.group',ondelete='cascade',),
        'datetime_from' : fields.datetime('From',),
        'datetime_to' : fields.datetime('To',),
        'participation_ids' : fields.many2many('groups.participation','groups_gaw_rel','gaw_id','participation_id',string='Participations'),
        'participation_domain' : fields.function(_domain_participation, arg=None, type='char', method=True, string='Participations domain'),
    }

    def change_group(self, cr, uid, ids, group_id, context=None):
        return {'value': {'participation_ids': [], 'participation_domain': self._default_domain_participation(cr, uid, {'active_id': group_id})}}
    
    def _default_group(self, cr, uid, context=None):
        if not context: context={}
        return context.get('active_id',False)

    def _default_domain_participation(self, cr, uid, context=None):
        if not context: context={}
        if not 'active_id' in context: return None
        domain=self.pool.get('groups.group')._domain_assignations(cr, uid, [context['active_id']]).items()[0][1]
        if not domain and type(domain)!=type([]): return None
        return "('id','in',"+str(list(domain.keys()))+")"

    _defaults = {
        'group_id' : _default_group,
        'participation_domain': _default_domain_participation,
        # participation_domain
    }
    
    def create_group_assignations(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            for part in obj.participation_ids:
                self.pool.get('groups.group_assignation').create(cr, uid, {'group_id': obj.group_id.id, 'datetime_from': obj.datetime_from, 'datetime_to': obj.datetime_to, 'participation_id': part.id})
        return True
    
groups_group_assignation_wizard()    
    
