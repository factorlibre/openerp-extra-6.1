# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (c) 2009 CCI  ASBL. (<http://www.ccilconnect.be>).
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

from osv import fields, osv
import time

class res_partner_state(osv.osv):
    _name = "res.partner.state"
    _description = 'res.partner.state'
    _columns = {
        'name': fields.char('Partner Status',size=50,required=True),
    }
res_partner_state()

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def _get_partner_state(self, cr, uid, ctx):
        ids = self.pool.get('res.partner.state').search(cr, uid, [('name','like', 'En Activité')])
        if ids:
            return ids[0]
        return False

    _columns = {
        'state_id':fields.many2one('res.partner.state','Partner State',help='status of activity of the partner'),
        
    }
    _defaults = {
        'state_id': _get_partner_state,
    }
res_partner()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _columns = {
        'magazine_subscription':fields.selection( [('never','Never'),('prospect','Prospect'),('personal','Personal'), ('postal','Postal')], "Magazine subscription"),
        'magazine_subscription_source':fields.char('Mag. Subscription Source',size=30),
    }
    _defaults = {
        'magazine_subscription': lambda *a: 'prospect',
    }
res_partner_address()

class res_partner_contact(osv.osv):
    _inherit = "res.partner.contact"
    _columns = {
        'magazine_subscription':fields.selection( [('never','Never'),('prospect','Prospect'),('personal','Personal'), ('postal','Postal')], "Magazine subscription"),
        'magazine_subscription_source':fields.char('Mag. Subscription Source',size=30),
    }
    _defaults = {
        'magazine_subscription': lambda *a: 'prospect',
    }
res_partner_contact()

class res_partner_job(osv.osv):
    _inherit = "res.partner.job"
    _columns = {
        'magazine_subscription':fields.selection( [('never','Never'),('prospect','Prospect'),('personal','Personal'), ('postal','Postal')], "Magazine subscription"),
        'magazine_subscription_source':fields.char('Mag. Subscription Source',size=30),
    }
    _defaults = {
        'magazine_subscription': lambda *a: 'prospect',
    }
res_partner_job()


class dated_photo(osv.osv):
    '''A photo of some details about partner's addresses and contacts at a precise date'''
    _name = "dated.photo"
    _description = "Photo of database at a precise date"
    _columns = {
        'name' : fields.char('Name',size=50,required=True),
        'datetime' : fields.datetime('Date',size=16,required=True,readonly=True),
        'photo_details_ids' : fields.one2many('photo.detail','photo_id','Postal subscribers'),
    }
    _defaults = {
        'datetime' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name' : lambda *a : 'Photo ' + time.strftime('%d-%m-%Y %H:%M:%S'),
    }

    def create(self, cr, uid, vals, *args, **kwargs):
        temp = super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
        self._take_one_shoot(cr, uid, temp )
        return temp

    def get_all_subscriber(self, cr, uid, context={}):
        cr.execute( """
                    SELECT p.id as partner_id, p.name, p.title, p.state_id, a.id as address_id, a.street, a.street2, a.zip, a.city, a.type
                    FROM res_partner p, res_partner_address a
                    WHERE p.id = a.partner_id AND a.magazine_subscription = 'postal'
                    ORDER BY p.id;
                    """)
        res = cr.fetchall()
        return res

    def _take_one_shoot(self, cr, uid, photo_id):
        obj_subscriber = self.pool.get('photo.detail')
        
        # TODO ? If we are not sure to take only one photo, at a time, we must delete all subscriber_details attached
        # before taking a new photo. Actually, only the create function of the object call this function
        # so it seems we don't need securing that point

        #Search all res.partner.address indicated as subscriber
        res = self.get_all_subscriber(cr, uid, {})

        #Record the current values of the fields copied in the SUMO DataBase
        for rec in res:
            obj_subscriber.create(cr, uid, {
                        'photo_id': photo_id,
                        'partner_id': rec[0],
                        'partner_contact_id': False,
                        'name': rec[1],
                        'title': rec[2],
                        'state_id': rec[3],
                        'address_id': rec[4],
                        'street': rec[5],
                        'street2': rec[6],
                        'zip': rec[7],
                        'city':rec[8],
                        })
        
        #Get the ID of the res_partner identifying the personal addresses
        obj = self.pool.get('res.partner')
        ids = obj.search(cr, uid, [('ref', '=', 'PERSONAL_ADDRESS' )])
        if ids:
            isolated_address_id = ids[0]
        
            #Search all res.partner.contact indicated as subscriber
            # First we extract the contacts subscriber ids
            ## TODO : perhaps, searching on the address.type = 'contact' is better than searching for the special partner_id...
            ##       if it's possible to have an address without res_partner associated (to check with Quentin)
            cr.execute( """
                    SELECT c.id as contact_id, c.name, c.first_name, a.id as address_id, a.street, a.street2, a.zip, a.city 
                        FROM res_partner_contact c, res_partner_job j, res_partner_address a, res_partner p
                        WHERE c.id in (
                                        SELECT c.id
                                            FROM res_partner_contact c
                                            WHERE ( c.magazine_subscription = 'postal' )
                                      )
                                    AND c.id = j.contact_id and j.address_id = a.id and p.id = %s and a.street != '' and a.zip != '';
                    """, isolated_address_id )
            res = cr.fetchall()
        
            #Record the current values of the fields copied in the SUMO DataBase
            #Take only the first address by order of the sequence (often the default address)
            oldID = 0
            for rec in res:
                if not rec[0] == oldID:
                 obj_subscriber.create(cr, uid, {
                            'photo_id': self.id,
                            'partner_id': False,
                            'address_id': rec[3], 
                            'partner_contact_id': rec[0],
                            'name': rec[1]+ ' ' + rec[2],
                            'title': '',
                            'state_id': '',
                            'street': rec[4],
                            'street2': rec[5],
                            'zip': rec[6],
                            'city':rec[7],
                            })
                oldID = rec[0]
            
    def compare_with_old_photo(self, cr, uid, ids ):
        if ids.length() == 2:
            # we search the older photo
            cr.execute( """
                        SELECT photo.id, photo.name, photo.datetime
                            FROM dated_photo photo
                            WHERE photo.id in ( %s, %s )
                            ORDER by photo.datetime;
                       """, (ids[0],ids[1]) )
            photos = cr.fetchall()
            
            cr.execute( """
                        SELECT partner_id, partner_contact_id, name, title, state_id, street, street2, zip, city
                            FROM photo_detail
                            WHERE photo_id = %s
                        """, photos[0].id )
            oldsubs = cr.fetchall()
            
            cr.execute( """
                        SELECT partner_id, partner_contact_id, name, title, state_id, street, street2, zip, city
                            FROM photo_detail
                            WHERE photo_id = %s
                        """, photos[1].id )
            newsubs = cr.fetchall()
dated_photo()

class subscriber_photo(osv.osv):
    '''Details about a res.partner.address or a res.parner.contact at a precise date. Only the details needed by the belgian software SUMO from the Post are recorded here'''
    _name = "photo.detail"
    _description = "Details about a photo of database"
    _columns = {
        'photo_id' : fields.many2one( 'dated.photo', 'Date de la photo' ), 
        'partner_id' : fields.many2one('res.partner','Partner',help='not used if directly addressed to a person'),
        'address_id' : fields.many2one('res.partner.address','Address'), 
        'partner_contact_id' : fields.many2one('res.partner.contact','Contact',help='only if directly addressed to one person'),
        'name' : fields.char('Name', size=64),
        'title': fields.char('Title', size=32),
        'state_id' : fields.many2one('res.partner.state','Partner State',help='status of activity of the partner'),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', size=24),
        'city': fields.char('City', size=128),
    }
subscriber_photo()

class photo_comparison(osv.osv):
    '''Capture the sum of all differences between two photos of subscribers'''
    _name = "photo.comparison"
    _description = "comparison between 2 photos"
    _columns = {
        'datetime' : fields.datetime('Date',size=16),
        'old_photo_id' : fields.many2one('dated.photo','Older Photo'),
        'new_photo_id' : fields.many2one('dated.photo','Newer Photo'),
        'diff_ids' : fields.one2many('photo.diff','comparison_id','Found differences'),
    }
    _defaults = {
        'datetime' : lambda *a: now().strftime('%Y-%m-%d %H-%M-%S'),
    }
    def get_name(self):
        return 'Comparaison du ' + self.datetime.strftime('%d-%m-%Y %H-%M-%S')
photo_comparison()

class photo_diff(osv.osv):
    '''Contains the result of the comparison between two states of a subscriber'''
    _name = "photo.diff"
    _description = "Details of comparison between 2 photos"
    _columns = {
        'comparison_id' : fields.many2one('photo.comparison','Comparison Date'),
        'type' : fields.char('Type',size=30),
        'old_values' : fields.text('Anciennes valeurs'),
        'new_values' : fields.text('Nouvelles valeurs'),
        'resource_id' : fields.integer('ID'),
        'model' : fields.char('DataBase',size=64),
        'oldid' : fields.char('Old ID',size=32),
    }
photo_diff()
