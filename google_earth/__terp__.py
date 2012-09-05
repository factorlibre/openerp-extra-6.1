# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
{
    "name" : "Google Earth/Map Module",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Others",
    "website" : "http://www.openerp.com",
    "depends" : ["sale"],
    "description": """
            This Module will includes following :

            * Layers with characteristics by regions (menu: Partners/Google Map/Earth)
                - country wise turnover display (low turnover=light red, high turnover=dark red) with information
                - partners display on map with its information
            * Display customers, whom country has colors by turnover (menu: Partners/Google Map/Earth)
                - partners display on map with its turnover
            * Most frequent delivery routes (menu: Partners/Google Map/Earth)
                - grouping of delivery by city and put route path on map with differnt color by number of deliveries
            * Network link kml file for dynamic updates of data on google earth.
            * directly open google map in your browser with different information.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["google_earth_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: