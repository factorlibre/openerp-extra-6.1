# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Enterprise Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://openerp.com>)
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

from osv import fields,osv
import datetime
class cleanup_wizard(osv.osv_memory):
    _name = 'memento_idea.cleanup.wizard'

    _columns = {
        'idea_age': fields.integer('Age'),
    }

    def do_cleanup(self,cr,uid,ids,context={}):
        idea_obj = self.pool.get('memento_idea.idea')
        for wiz in self.browse(cr,uid,ids):
            days = wiz.idea_age
            if days <= 3:
                raise osv.except_osv('UserError','Please select a larger value')
            limit = datetime.date.today() - datetime.timedelta(days=days)
            ids_to_del = idea_obj.search(cr,uid,
                [('create_date', '<' , limit.strftime('%Y-%m-%d 00:00:00'))],context=context)
            idea_obj.unlink(cr,uid,ids_to_del)
        return {'type': 'ir.actions.act_window_close'}

cleanup_wizard()
