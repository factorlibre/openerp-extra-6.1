##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Serpent Consulting Services (<http://www.serpentcs.com>).
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

from osv import osv, fields
import netsvc
import time

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def action_in_production(self, cr, uid, ids):
        wf_service = netsvc.LocalService("workflow")
        self.write(cr, uid, ids, {'state': 'in_production', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')})
        for obj in self.browse(cr, uid, ids):
            if obj.workcenter_lines:
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', obj.workcenter_lines[0].id, 'button_start_working', cr)
        return True

mrp_production()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: