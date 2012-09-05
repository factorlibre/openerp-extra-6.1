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

class purchase_civilengineering(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'work_id':fields.many2one('civil_engineering.work','Work'),
    }

purchase_civilengineering()
