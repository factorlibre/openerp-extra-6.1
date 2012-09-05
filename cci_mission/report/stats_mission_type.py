# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from report import report_sxw
import time

class stats_mission_type(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stats_mission_type, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time, 
            'get_missions_states': self._get_missions_states, 
            'get_total_certi': self._get_total_certi, 
            'get_total_legalization':self._get_total_legalization, 
            'get_total_ata':self._get_total_ata, 
            'get_total_ambassy':self._get_total_embassy
        })

    def _get_missions_states(self,d1,d2):
            self.cr.execute("select t.section, count(t.id) as no_certi, sum(d.goods_value) as no_goods,  \
                            sum(c.total) as total_sub, d.type_id, t.name  \
                            from cci_missions_dossier as d,cci_missions_dossier_type as t, cci_missions_certificate as c \
                            where c.dossier_id = d.id and d.type_id=t.id  and ( d.date::date  BETWEEN '%s' AND '%s' )\
                            group by type_id,t.name,t.section, t.id" % (d1, d2))
            res_cert = self.cr.dictfetchall()

            self.cr.execute("select t.section, count(t.id) as no_certi, sum(d.goods_value) as no_goods,  \
                            sum(l.total) as total_sub, d.type_id, t.name  \
                            from cci_missions_dossier as d,cci_missions_dossier_type as t, cci_missions_legalization as l \
                            where l.dossier_id = d.id and d.type_id=t.id  and ( d.date::date  BETWEEN '%s' AND '%s' )\
                            group by type_id,t.name,t.section, t.id" % (d1, d2))
            res_leg = self.cr.dictfetchall()

            self.cr.execute("select t.section, count(t.id) as no_certi, sum(goods_value) as no_goods,  \
                            sum(sub_total) as total_sub, type_id, t.name  \
                            from cci_missions_ata_carnet as d,cci_missions_dossier_type as t \
                            where d.type_id=t.id  and ( d.creation_date::date  BETWEEN '%s' AND '%s' )\
                            group by type_id,t.name,t.section, t.id" % (d1, d2))
            res_ata = self.cr.dictfetchall()
            #self.cr.execute("select count(e.id) as no_certi, sum(l.customer_amount) as total_sub, s.name\
            #                from cci_missions_embassy_folder as e \
            #                left join cci_missions_embassy_folder_line as l \
            #                on e.id=l.folder_id \
            #                left join cci_missions_site as s \
            #                 on s.id=e.site_id where (e.embassy_date  BETWEEN '%s' AND '%s' ) \
            #                 group by s.name" % (d1, d2))
            self.cr.execute("select count(e.id) as no_certi, sum( l.total_sub ) as total_sub, s.name from cci_missions_embassy_folder as e \
                            left join \
                                ( select folder_id, sum( customer_amount-courier_cost ) as total_sub from cci_missions_embassy_folder_line group by folder_id ) as l \
                            on e.id=l.folder_id \
                            left join cci_missions_site as s on s.id=e.site_id \
                            where (e.embassy_date  BETWEEN '%s' AND '%s' ) group by s.name;" % (d1, d2))
            res_ata2 = self.cr.dictfetchall()
            temp_list = []
            for i in res_ata2:
                i.update({'section':'folder'})
                temp_list.append(i)
            return res_cert + res_leg + res_ata + temp_list

    def _get_total_certi(self,d1,d2):
            self.cr.execute("select t.section, count(t.id) as no_certi, sum(goods_value) as no_goods, \
                            sum(c.total) as total_sub \
                             from cci_missions_dossier as d,cci_missions_dossier_type as t, cci_missions_certificate as c \
                            where c.dossier_id = d.id and d.type_id=t.id  and t.section=\'certificate\' \
                            and (d.date::date  BETWEEN '%s' AND '%s' )\
                            group by t.section" % (d1, d2))
            res_ata = self.cr.dictfetchall()
            return res_ata

    def _get_total_legalization(self,d1,d2):
            self.cr.execute("select t.section, count(t.id) as no_certi, sum(goods_value) as no_goods, \
                            sum(l.total) as total_sub \
                             from cci_missions_dossier as d,cci_missions_dossier_type as t, cci_missions_legalization as l \
                            where l.dossier_id = d.id and d.type_id=t.id  and t.section=\'legalization\' \
                            and (d.date::date  BETWEEN '%s' AND '%s' )\
                            group by t.section" % (d1, d2))
            res_ata = self.cr.dictfetchall()
            return res_ata

    def _get_total_ata(self,d1,d2):
            self.cr.execute("select t.section, count(t.id) as no_certi, sum(goods_value) as no_goods, \
                            sum(sub_total) as total_sub \
                             from cci_missions_ata_carnet as d,cci_missions_dossier_type as t \
                            where d.type_id=t.id  and t.section=\'ATA\' \
                            and (d.creation_date::date  BETWEEN '%s' AND '%s' )\
                            group by t.section" % (d1, d2))
            res_ata = self.cr.dictfetchall()
            return res_ata

    def _get_total_embassy(self,d1,d2):
            #self.cr.execute("select count(e.id) as no_certi, sum(l.customer_amount) as total_sub  \
            #                from cci_missions_embassy_folder as e \
            #                left join cci_missions_embassy_folder_line as l \
            #                    on e.id=l.folder_id \
            #                left join cci_missions_site as s \
            #                    on s.id=e.site_id\
            #                 where (e.embassy_date::date BETWEEN '%s' AND '%s' )" % (d1, d2))
            self.cr.execute("select count(e.id) as no_certi, sum( l.total_sub ) as total_sub from cci_missions_embassy_folder as e \
                            left join \
                                ( select folder_id, sum( customer_amount-courier_cost ) as total_sub from cci_missions_embassy_folder_line group by folder_id ) as l \
                            on e.id=l.folder_id \
                            left join cci_missions_site as s on s.id=e.site_id \
                            where (e.embassy_date::date BETWEEN '%s' AND '%s' )" % (d1, d2))
            res_ata = self.cr.dictfetchall()
            if res_ata[0]['total_sub'] is None:
                res_ata = {}
            return res_ata

report_sxw.report_sxw('report.stats.mission.type', 'cci_missions.certificate', 'addons/cci_mission/report/stats_mission_type.rml', parser=stats_mission_type, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
