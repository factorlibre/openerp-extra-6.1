# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Enterprise Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://openerp.com>).
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

from osv import osv
from osv import fields

class category(osv.osv):          # inherit from osv: create/write/read/delete
    _name = 'memento_idea.category'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'description': fields.text('Description', help='Description', translate=True ),
        'active': fields.boolean('Active', select=True),
        'parent_id': fields.many2one('memento_idea.category','Parent Category',ondelete="set null"),
        'child_ids': fields.one2many('memento_idea.category','parent_id','Child Categories'),
    }

    _defaults = {
        'active': lambda *a: True,
    }

category()


class idea(osv.osv):          # inherit from osv: create/write/read/delete
    _name = 'memento_idea.idea'     # meaningful name for table in lists

    _columns = {
        'name': fields.char('Title', size=64, required=True, translate=True),
        'state': fields.selection([
                ('draft','Draft'), ('confirmed','Confirmed'),('closed','Closed')], 
                readonly=True, string='State'),
        'description': fields.text('Description', readonly=True, required=True,
                       states={'draft': [('readonly', False)]} ),
        'invent_date': fields.date('Invent date'),
        'inventor_id': fields.many2one('res.partner','Inventor'),
        'inventor_country': fields.related('inventor_id','country',
                            readonly=True, type='many2one',
                            relation='res.country', string='Country'),
        'sponsor_ids': fields.many2many('res.partner','idea_sponsor_rel',
                                        'idea_id','sponsor_id','Sponsors'),
        'score': fields.float('Score', digits=(2,1)),
        'active': fields.boolean('Active', select=True),
        'picture': fields.binary('Picture', help='Worth 1000 words', filters='*.png,*.gif'),
        'category_id': fields.many2one('memento_idea.category','Category'),
        'sequence': fields.integer('Seq'),
    }

    _defaults = {
        'active': lambda *a: True,
        'state': lambda *a: 'draft',
    }

    def _check_name(self,cr,uid,ids):
        for idea in self.browse(cr, uid, ids):
            return reduce(lambda x,y:x and y not in idea.name,['spam','eggs'],1)
        
    def action_confirm(self,cr,uid,ids,context={}):
        self.write(cr,uid,ids,{'state':'confirmed'},context=context)
        
    def action_closed(self,cr,uid,ids,context={}):
        self.write(cr,uid,ids,{'state':'closed'},context=context)

    _sql_constraints = [('name_uniq','unique(name)', 'Idea must be unique!')]

    _constraints = [(_check_name,'Please be polite!', ['name'])]

idea()


class vote(osv.osv):
    _name = 'memento_idea.vote'
    _rec_name = 'id'
    _columns = {
        #Hack to avoid declaring a dummy unique name -> use id as _rec_name
        'id': fields.integer('Id'),
        'vote': fields.float('Vote',digits=(2,1)),
        'partner_id': fields.many2one('res.partner','Partner'),
        'idea_id': fields.many2one('memento_idea.idea','Idea'),
    }
vote()


# We need a subclass of our main idea class to break the dependency cycle
# between ideas and votes. This is just a python trick, but there will only
# ever be one main idea class/object in our module, since we use class inheritance.
class idea2(osv.osv):
    _inherit = 'memento_idea.idea'

    # Function used to find the idea to update whenever a trigger is activated
    # on a vote object. (See vote_avg and vote_num function fields defined below) 
    def _get_idea_from_vote(self,cr,uid,ids,context={}):
     res = {}
     vote_ids = self.pool.get('memento_idea.vote').browse(cr,uid,ids,context=context)
     for v in vote_ids:
       res[v.idea_id.id] = True  # Store the idea id in a set
     return res.keys()

    def _compute(self,cr,uid,ids,field_name,arg,context={}):
     res = {}
     for idea in self.browse(cr,uid,ids):
       vote_num = len(idea.vote_ids)
       vote_sum = sum([v.vote for v in idea.vote_ids])
       res[idea.id] = {
          'vote_num': vote_num,
          'vote_avg': (vote_sum/vote_num) if vote_num else 0.0,
       }
     import traceback
     traceback.print_stack()
     return res

    _columns = { 
        'vote_ids': fields.one2many('memento_idea.vote', 'idea_id', 'Votes'),
        'vote_avg': fields.function(_compute, method=True,string='Votes Average',
            store = {
                  'memento_idea.vote': (_get_idea_from_vote,['vote'],10),
               }, multi='votes'),
        'vote_num': fields.function(_compute, method=True,string='Vote Count',
            store = {
                  'memento_idea.vote': (_get_idea_from_vote,['vote'],10),
               }, multi='votes'),
    }
idea2()