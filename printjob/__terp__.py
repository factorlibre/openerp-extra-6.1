# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2007 Ferran Pegueroles <ferran@pegueroles.com>
#    Copyright (c) 2009 Albert Cervera i Areny <albert@nan-tic.com>
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
    "name" : "PrintJob",
    "author" : "Pegueroles SCP & NaN",
    "version" : "1.0",
    "website" : "http://www.pegueroles.com",
    "depends" : ["base"],
    "description": """This module updates OpenERP printing by adding the following features:
* Enables batch printing 
* Correct memory leak when printing crashes
* Permits reprinting lost PDFs
* Possibilty to send jobs to a printer attached to the server 
* Settings can be configured globaly, per user, per report and per user and report.
    """,
    "init_xml" : [],
    "update_xml" : [
        "printjob_view.xml",                    
        "printjob_data.xml",                    
        "security/printjob_security.xml",
    ],
    "category" : "base/printjob",
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
