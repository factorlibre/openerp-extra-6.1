from osv import fields,osv

class res_users(osv.osv):
    _inherit = 'res.users'
    
    _columns = {
        'project_ids': fields.many2many('project.project', 'project_user_rel', 'uid', 'project_id', 'Projects',
            help="These are the projects in which the user has been chosen as one of the members"),
    }

res_users()