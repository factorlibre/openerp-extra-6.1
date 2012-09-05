# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Albert Cervera i Areny <albert@nan-tic.com>
#    $Id$
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
    "name" : "E-mail Purchase",
    "version" : "1.0",
    "depends" : ["smtpclient","purchase"],
    "author" : "NaN·tic",
    "website" : "www.NaN-tic.com",
    "license" : "GPL-3",
    "description": """Use Email client module to send to suppliers the selected purchase orders attached by Email.

  * The invoice and contact emails addresses are proposed
  * An email subject and text with the user signature are proposed
  * Later, the emails addresses, subject and text can be modified
  * A partner event is created with information of the email (partner,
    description, channel, document, user)
  * Historical and statistical data is recorded in the smtpclient module

  The modules has been implemented based on email_sale. Indeed the code is almost the same.
""",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["email_purchase_wizard.xml"],
    "active": False,
    "installable": True
}
