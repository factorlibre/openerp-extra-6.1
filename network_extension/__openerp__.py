# -*- coding: utf-8 -*-
##############################################################################
#
#    network_extension module for OpenERP
#    Copyright (C) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#       Jordi Esteve <jesteve@zikzakmedia.com> All Rights Reserved.
#    Copyright (C) 2009-2011 SYLEAM (http://syleam.fr)
#       Christophe Chauvet <christophe.chauvet@syleam.fr> All Rights Reserved.
#
#    This file is a part of network_extension
#
#    network_extension is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    network_extension is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Network Management Extension",
    "version": "1.0.1",
    "author": "Zikzakmedia SL, SYLEAM",
    "category": "Enterprise Specific Modules/Information Technology",
    "website": "www.zikzakmedia.com",
    "license": "AGPL-3",
    "depends": ["network"],
    'init_xml': ['network_protocol_data.xml'],
    "demo_xml": [],
    "update_xml": [
        'security/ir.model.access.csv',
        "network_view.xml",
    ],
    "description": """
Organize your software and configurations.
    - Additional network information: IP, domain, DNS, gateway
    - Protocols
    - Services
    - Ports
    - Public and private URLs
    - Password encryption

System dependency: package python-crypto required.""",
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
