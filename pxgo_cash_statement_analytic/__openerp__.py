# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2010 Pexego Sistemas Informáticos. All Rights Reserved
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
        "name" : "Pexego - Analytic in Cash Statements",
        "version" : "1.0",
        "author" : "Pexego for Igalia (http://www.igalia.com/)",
        "website" : "http://www.pexego.es",
        "category" : "Enterprise Specific Modules",
        "description": """
Extends the Cash Statements to add support for analytic accounting.

A analytic account field will be added to cash statement line types, allowing
the user to preset analytic accounts for the line types.
            """,
        "depends" : [
                'base',
                'account',
                'pxgo_cash_statement',
                'pxgo_bank_statement_analytic'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                'cash_statement_view.xml',
            ],
        "installable": True,
        'active': False

}
 
