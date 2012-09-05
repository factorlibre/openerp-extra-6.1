# encoding: utf-8
{
	"name" : "Account Jasper Reporting",
	"version" : "0.1",
	"description" : "This module adds several Jasper Reports to spanish accounting system.",
	"author" : "NaN·tic",
	"website" : "http://www.NaN-tic.com",
	"depends" : [
		'jasper_reports',
		'account'
	],
	"category" : "Accounting",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		'jasper_view.xml',
		'jasper_report.xml'
	],
	"active": False,
	"installable": True
}
