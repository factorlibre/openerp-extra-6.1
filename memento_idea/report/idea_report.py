# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Enterprise Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://openerp.com>).
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


from report import report_sxw

#
# Reporting on ideas
# 
class idea_report(report_sxw.rml_parse):

    def weather_forecast(self, *params):
        return "Today's forecast: rainy with 50km/h winds (%r)" % (params,)
    
    def __init__(self,cr,uid,name,context=None):
        if not context: context = {}
        super(idea_report, self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
            # Dumb examples, just to get the idea... ;-)
            'weather_forecast': self.weather_forecast,
            'report_designer': 'OpenERP Report Designer',
        })

report_sxw.report_sxw('report.idea.simple.report',  # Name of report (must start with 'report')
                      'memento_idea.idea',          # Model name of object on which this report is defined
                      'addons/memento_idea/report/idea.rml', # Path to RML file, rooted in server/bin
                      parser=idea_report,           # Bind custom report parser
                      header=True,                  # Whether to include report header/footer (Default=True)
                      ) 