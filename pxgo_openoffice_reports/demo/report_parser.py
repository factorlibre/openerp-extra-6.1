# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

"""Add dummy function to context, it prints Hi! when you call it"""

from addons.pxgo_openoffice_reports.openoffice_report import openoffice_report, OOReport

class report_parser(OOReport):
    """Add dummy function to context, it prints Hi! when you call it"""
    def get_report_context(self):
        """Add dummy function to context, it prints Hi! when you call it"""
        res = super(report_parser, self).get_report_context()
        res.update({
            'print_hi': self.print_hi,
        })
        return res

    def print_hi(self):
        """Print Hi!"""
        res = "Hi !"
        return res

openoffice_report('report.pxgo_openoffice_reports.partner_demo_ods_not_auto', 'res.partner', parser=report_parser)