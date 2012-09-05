# -*- encoding: utf-8 -*-
{
	"name" : "Partner Risk Analysis",
	"version" : "0.1",
	"description" : """This module adds a new button in the partner form to analyze current state of a partner risk.
It reports current information regarding amount of debt in invoices, orders, etc.

It also modifies the workflow of sale orders by adding a new step when partner's risk is exceeded.

Developed for Trod y Avia, S.L.""",
	"author" : "NaN·tic",
	"website" : "http://www.NaN-tic.com",
	"depends" : [ 
		'base', 
		'account', 
		'sale',
		'account_payment',
	], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
        'wizard/open_risk_window_view.xml',
		'risk_view.xml',
		'sale_view.xml',
		'sale_workflow.xml'
	],
	"active": False,
	"installable": True
}
