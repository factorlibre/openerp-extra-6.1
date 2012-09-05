# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2011  NaN Projectes de Programari Lliure S.L.
#                   (http://www.nan-tic.com) All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name" : "NaN Sale 3 Discounts.",
    "version" : "0.1",
    "description" : """
            Extension of sale. This module adds those functionalities:
                - Adds 3 diferent discounts on sale order lines
                - Calculate resulting discount based on the other discounts
        """,
    "author" : "NaN·tic",
    "website" : "http://www.NaN-tic.com",
    "depends" : [ 
        'account',
        'sale',
        'stock',
    ], 
    "category" : "Generic Modules/Sale",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'sale_view.xml',
    ],
    "active": False,
    "installable": True
}

