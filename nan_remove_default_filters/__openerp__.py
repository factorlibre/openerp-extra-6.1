# encoding: utf-8
{
    "name" : "Remove Default Filters",
    "version" : "1.0",
    "description" : """This module removes default filters from several search views:
- Invoices
- Sale orders
- Purchase orders
- Purchase requisitions""",
    "author" : "NaN·tic",
    "website" : "http://www.NaN-tic.com",
    "depends" : [
        'crm',
        'purchase_requisition',
        'sale',
     ],
    "category" : "Useability",
    "demo_xml" : [],
    "init_xml" : [
    ],
    "update_xml" : [
        'account_view.xml',
        'purchase_view.xml',
        'sale_view.xml',
        'crm_view.xml',
    ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
