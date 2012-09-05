# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#
##############################################################################
{
    "name": "Complete pricelist overview",
    "version": "1.0",
    "depends": ["product_pricelist_fixed_price"],
    "author": "Marco Dieckhoff, BREMSKERL",
    "category": "Generic Modules/Inventory Control",
    "description": """Complete pricelist overview:
    Improves views to manage pricelist items quickly.
    """,
    "init_xml": [],
    'update_xml': [
        "pricelist_view.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
