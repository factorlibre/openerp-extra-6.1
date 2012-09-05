# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
# runs a sforce SOQL query and saves the results as a csv file.
import sys
import string
import beatbox
import xmltramp
import netsvc
logger = netsvc.Logger()

sf = beatbox._tPartnerNS
svc = beatbox.Client()

def buildSoql(sobjectName):
	dr = svc.describeSObjects(sobjectName)
	soql = ""
	for f in dr[sf.fields:]:
		if len(soql) > 0: soql += ','
		soql += str(f[sf.name])
	return "select " + soql + " from " + sobjectName

def printColumnHeaders(queryResult):
	needsComma = 0
	# note that we offset 2 into the records child collection to skip the type and base sObject id elements
	for col in queryResult[sf.records][2:]:
		if needsComma: print ',',
		else: needsComma = 1
		
def export(username, password, objectOrSoql):
	svc.login(username, password)
	if string.find(objectOrSoql, ' ') < 0:
		soql = buildSoql(objectOrSoql)
	else:
		soql = objectOrSoql
	
	qr = svc.query(soql)
	while True:
		if printHeaders: printColumnHeaders(qr); printHeaders = 0
		for row in qr[sf.records:]:
			needsComma = False
			for col in row[2:]:
				if needsComma: logger.notifyChannel(',',)
				else: needsComma = True
				logger.notifyChannel(str(col),)
		if str(qr[sf.done]) == 'true': break
		qr = svc.queryMore(str(qr[sf.queryLocator]))

if __name__ == "__main__":

	if len(sys.argv) != 4:
		logger.notifyChannel("usage is export.py <username> <password> [<sobjectName> || <soqlQuery>]")
	else:
		export(sys.argv[1], sys.argv[2], sys.argv[3])
