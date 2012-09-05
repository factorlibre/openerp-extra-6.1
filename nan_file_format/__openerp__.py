# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2010   Àngel Àlvarez 
#                      NaN Projectes de programari lliure S.L.
#                      (http://www.nan-tic.com) All Rights Reserved.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
	"name" : "Export File Format Configuration",
	"version" : "0.1",
	"description" : """
        Definition of fields with the format for exporting files. Allow:
        - Fixed or variable length files
        - Alignment of fields
        - Formats for numeric fields
    
        Definition of the model where the information extracted, directory and file name where it pulled.
        """,
	"author" : "NaN·tic",
	"website" : "http://www.NaN-tic.com",
	"depends" : [
        'base',
        #'delivery',
    ], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [ 'format_view.xml' ],
	"active": False,
	"installable": True
}
