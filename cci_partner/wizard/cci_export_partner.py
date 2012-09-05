# -*- coding: utf-8 -*-
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

import wizard
import pooler
import pyExcelerator as xl
import StringIO
import base64
import time
from tools.translate import _

form = '''<?xml version="1.0"?>
<form string="Export Partners">
    <separator string="Export partners data for SUMO software" colspan="4"/>
    <newline/>
    <!--field name="date_from" colspan="4"/>
    <field name="date_to" colspan="4"/-->
</form>'''

form_extract = '''<?xml version="1.0"?>
<form string="Extract data">
    <separator string="Export data in excel file for SUMO software" colspan="4"/>
    <newline/>
</form>'''


view_form_finish="""<?xml version="1.0"?>
<form string="Export Progenus Number">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" colspan="3" readonly="1" filename="file_name"/>
        <label align="0.0" string="Save this document to a .xsl file and open it with\n your favorite spreadsheet software. The file\n encoding is UTF-8." colspan="4"/>
    </group>
</form>"""

fields_form_finish={
        'data': {'string':'File', 'type':'binary'},
        'file_name':{'string':'File Name', 'type':'char'}
    }

fields = {
}

def _make_calculation(self, cr, uid, data, context):
    form = data['form']
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(cr, uid, [('membership_state','in', ('free','paid','invoiced'))])
    part_address_chg_obj = pool.get('res.partner.address.change')
    part_chg_obj = pool.get('res.partner.change')
    part_photo_obj = pool.get('res.partner.photo')
    cr.execute('select id from res_partner_photo order by date desc limit 1')
    last_photo_id = cr.fetchone()
    last_photo_id = last_photo_id and last_photo_id[0] or False
    part_address_obj = pool.get('res.partner.address')
    part_lost_obj = pool.get('res.partner.address.lost')
    part_address_new_obj = pool.get('res.partner.address.new')
    part_state_obj = pool.get('res.partner.state.register')
    postal_addr = []
    address_l = []
    address_def = []
    list_lost_out = []
    photo_id = part_photo_obj.create(cr, uid, {})
    for partner in partner_obj.browse(cr, uid, partner_ids):
        postal_addr = [x.id for x in partner.address if x.magazine_subscription in ('postal','personal')]
        if not len(postal_addr):
            for address in partner.address:
                never_addr = [x.id for x in partner.address if x.state in ('never')]
                if not never_addr and address.type=='default':
                    part_address_new_obj.create(cr, uid, {'code':partner.ref,
                                                        'name':partner.id,
                                                        'address':(address.street or '')+ ' ' + (address.zip or '')+ '  ' + (address.city or ''),
                                                        'address_id':address.id,
                                                        'photo_id' : photo_id,
                                                        'state_activity':partner.state_id and partner.state_id.id or False
                    })
                    part_address_obj.write(cr, uid, [address.id],{'magazine_subscription':'postal'})
    if last_photo_id:
        """
        Create entries for losts partners
        """
        cr.execute("select id from res_partner where (state_id is null or state_id not in (1)) and id not in (select partner_id from res_partner_address_lost)")
        for part_id in cr.dictfetchall():
            partner_id = partner_obj.browse(cr, uid, part_id['id'])
            if len(partner_id.address):
                address_def = [x.id for x in partner_id.address if x.type == 'default']
                part_lost_obj.create(cr, uid, {'name': partner_id.ref,
                                            'address_id': address_def and address_def[0] or False,
                                            'partner_id': partner_id.id,
                                            'state_activity' : partner_id.state_id and partner_id.state_id.id or False,
                                            'photo_id' : photo_id})
        """
        Create entries for partners changes states
        """
        for state_item in part_photo_obj.browse(cr, uid, last_photo_id).partner_state_ids:
            if state_item.new_state.id != state_item.partner_id.state_id.id:
                address_l = [x.id for x in state_item.partner_id.address if x.type == 'default']
                part_state_obj.create(cr, uid, {'old_state': state_item.new_state and state_item.new_state.id,
                                                'new_state': state_item.partner_id.state_id.id,
                                                'name' : state_item.partner_id.ref,
                                                'partner_id' : state_item.partner_id.id,
                                                'address_id' : (address_l and address_l[0]) or (state_item.address_id and state_item.address_id.id) or False,
                                                'photo_id' : photo_id})
                list_lost_out.append(state_item.partner_id.id)

        """
        Create entries for changed adresses
        """
        for adr_item in part_photo_obj.browse(cr, uid, last_photo_id).address_chg_ids:
            address_zip =  adr_item.address_id.zip_id and adr_item.address_id.zip_id.city or ''
            if adr_item.new_address != ((adr_item.address_id.street or '')+ '- ' + address_zip):
                part_address_chg_obj.create(cr, uid, {'old_address': adr_item.new_address,
                                                'new_address' : (adr_item.address_id.street or '')+ '- ' + address_zip,
                                                'code' : adr_item.address_id and adr_item.address_id.partner_id and adr_item.address_id.partner_id.ref or '',
                                                'name' : adr_item.address_id and adr_item.address_id.partner_id.id or False,
                                                'address_id' : adr_item and adr_item.address_id.id or False,
                                                'photo_id' : photo_id})


        """
        Create entries for new adresses
        """
        cr.execute("select id from res_partner_address where magazine_subscription = 'postal' and id not in (select address_id from res_partner_address_new where address_id is not null)")
        for item in cr.dictfetchall():
            address_id = part_address_obj.browse(cr, uid, item['id'])
            if address_id.partner_id.state_id.id in (1):
                address_zip =  address_id.zip_id and address_id.zip_id.city or ''
                part_address_new_obj.create(cr, uid, {'name': address_id.partner_id.id,
                                                    'address_id': address_id.id,
                                                    'code': address_id.partner_id.ref,
                                                    'state_activity' : address_id.partner_id.state_id and address_id.partner_id.state_id.id or False,
                                                    'address': (address_id.street or '') + '- ' + address_zip,
                                                    'photo_id' : photo_id})

        """
        Create entries for changed partner names
        """
        for adr_item in part_photo_obj.browse(cr, uid, last_photo_id).partner_chg_ids:
            if adr_item.address_id and adr_item.address_id.partner_id and (adr_item.address_id.partner_id.id not in list_lost_out):
                partner_name = (adr_item.address_id and adr_item.address_id.partner_id.name + ' ') + (adr_item.address_id.name and (adr_item.address_id.name or '') or '')
                if (adr_item.name).strip() != partner_name.strip():
                    part_chg_obj.create(cr, uid, {'old_name': adr_item.name,
                                                'name': partner_name,
                                                'code' : adr_item.address_id and adr_item.address_id.partner_id and adr_item.address_id.partner_id.ref or '',
                                                'address_id' : adr_item and adr_item.address_id.id or False,
                                                'photo_id' : photo_id})



    return {}

def _make_excel_file(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    workBookDocument = xl.Workbook()
    docSheet1 = workBookDocument.add_sheet("Disparus")
    docSheet2 = workBookDocument.add_sheet("Nouveaux")
    docSheet3 = workBookDocument.add_sheet("Chg de noms")
    docSheet4 = workBookDocument.add_sheet("Chg d Etats")
    docSheet5 = workBookDocument.add_sheet("Chg d'Adresses")
    part_photo_obj = pool.get('res.partner.photo')
    partner_obj = pool.get('res.partner')
    cr.execute("select id from res_partner_photo order by date desc")
    photo_id = cr.fetchone()
    photo_id = photo_id and photo_id[0] or False
    photo_rec = part_photo_obj.browse(cr, uid, photo_id)

    list_losts = [u"Clé","Nom - Forme","Adresse","Etat"]
    for header_num,header_item in enumerate(list_losts):
        docSheet1.write(0, header_num, header_item)

    """
        Data of lost partners
    """
    row_count = 0
    for rec in photo_rec.partner_lost_ids:
        row_count += 1
        docSheet1.write(row_count,0,(rec.partner_id.ref or ''))
        docSheet1.write(row_count,1,rec.partner_id.name)
        address_def = [((x.street or '')+ '- ' + (x.zip_id and x.city or '')) for x in rec.partner_id.address if x.type == 'default']
        if len(address_def):
            docSheet1.write(row_count,2,address_def[0])
        docSheet1.write(row_count,3,(rec.partner_id.state_id and rec.partner_id.state_id.name or ''))

    """
        Data of New partners
    """
    list_new = [u"Clé","Nom - Forme","Adresse","Etat"]
    for header_num,header_item in enumerate(list_new):
        docSheet2.write(0, header_num, header_item)
    row_count = 0
    for rec in photo_rec.partner_new_ids:
        row_count += 1
        docSheet2.write(row_count,0,(rec.address_id.partner_id and rec.address_id.partner_id.ref or ''))
        docSheet2.write(row_count,1,rec.address_id.partner_id and rec.address_id.partner_id.name or '')
        docSheet2.write(row_count,2,rec.address or '')
        docSheet2.write(row_count,3,(rec.address_id.partner_id and rec.address_id.partner_id.state_id and rec.address_id.partner_id.state_id.name or ''))

    """
        Data of Changed partners
    """
    list_chg = [u"Clé","Ancien Nom","Nouveau nom","Adresse"]
    for header_num,header_item in enumerate(list_chg):
        docSheet3.write(0, header_num, header_item)
    row_count = 0
    for rec in photo_rec.partner_chg_ids:
        row_count += 1
        docSheet3.write(row_count,0,(rec.address_id.partner_id.ref or ''))
        docSheet3.write(row_count,1,rec.address_id.partner_id.name)
        docSheet3.write(row_count,2,(rec.name or ''))
        address = (rec.address_id.street or '')+ ' ' + (rec.address_id.zip or '')+ '  ' + (rec.address_id.city or '')
        docSheet3.write(row_count,3,address)

    """
        Data of Changed states
    """
    list_chg_adr = [u"Clé","Nom - Forme","Ancien Etat","Nouvel Etat","Adresse"]
    for header_num,header_item in enumerate(list_chg_adr):
        docSheet4.write(0, header_num, header_item)
    row_count = 0
    for rec in photo_rec.partner_state_ids:
        row_count += 1
        docSheet4.write(row_count,0,(rec.address_id.partner_id.ref or ''))
        docSheet4.write(row_count,1,(rec.address_id.partner_id.name or ''))
        docSheet4.write(row_count,2,(rec.new_state and rec.new_state.name or ''))
        docSheet4.write(row_count,3,(rec.partner_id and rec.partner_id.state_id and rec.partner_id.state_id.name or ''))
        address = (rec.address_id.street or '')+ ' ' + (rec.address_id.zip or '')+ '  ' + (rec.address_id.city or '')
        docSheet4.write(row_count,4,address)

    """
        Data of Changed Adresses
    """
    list_chg_adr = [u"Clé","Nom - Forme","Ancienne Adresse","Nouvelle Adresse"]
    for header_num,header_item in enumerate(list_chg_adr):
        docSheet5.write(0, header_num, header_item)
    row_count = 0
    for rec in photo_rec.address_chg_ids:
        row_count += 1
        docSheet5.write(row_count,0,(rec.address_id.partner_id.ref or ''))
        address_def = [x.name for x in rec.address_id.partner_id.address if x.type == 'default']
        address_def = address_def and address_def[0] or ''
        docSheet5.write(row_count,1,rec.address_id and (rec.address_id.partner_id.name +' '+ address_def))
        docSheet5.write(row_count,2,rec.old_address or '')
        docSheet5.write(row_count,3,rec.new_address or '')
    file=StringIO.StringIO()
    out=workBookDocument.save(file)
    out=base64.encodestring(file.getvalue())
    return {'data': out , 'file_name':'export_sumo_file%s.xsl'%time.strftime('%Y-%m-%d')}

class wizard_export_partner(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('compare','Compare with last data')]}
        },
        'compare': {
            'actions': [_make_calculation],
            'result': {'type':'form', 'arch':form_extract, 'fields':fields, 'state':[('end','Cancel'),('extract','Extract last last data in Excel File')]}
        },
        'extract': {
            'actions': [_make_excel_file],
            'result' : {'type' : 'form',
                        'arch' : view_form_finish,
                        'fields' : fields_form_finish,
                        'state': [('end', 'Close', 'gtk-cancel', True)]}
        },
    }
wizard_export_partner('cci.export.partner')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
