# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA 2011
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


{
    'name': 'Partner Merger for external referentials',
    'version': '1.0',
    'category': 'Generic Modules/Base',
    'description': """
Extend the module base_partner_merge and add special purposes to use it with base_external_referentials module :
  - Blocks the merge of two partners / addresses created from an external referential
  - Update external links (ir_model_data) to refers to the new created partner / address

To merge 2 partners, select them in the list view and execute the Action "Merge Partners".
To merge 2 addresses, select them in the list view and execute the Action "Merge Partner Addresses" or use the menu item :
 Partners / Configuration / Merge Partner Addresses

    """,
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['base', 'base_partner_merge', 'base_external_referentials'],
    'init_xml': [],
    'update_xml': [
                   ],
    'demo_xml': [],
    'installable': True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
