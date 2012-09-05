# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import pygtk
pygtk.require("2.0")
import gtk
import xmlrpclib
from lxml import etree
import sys, dia
import math

def warning(msg, type=gtk.MESSAGE_INFO):
    dialog = gtk.MessageDialog(None,
      gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
      type, gtk.BUTTONS_OK,
      msg)
    dialog.run()
    return dialog.destroy()

class window(object):
    def __init__(self):
        self.dia = gtk.Dialog(
            'Open ERP View',
            None,
            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT
        )
        #self.dia.set_property('default-width', 760)
        #self.dia.set_property('default-height', 500)

        self.but_cancel = self.dia.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)

        table = gtk.Table(2,6)
        row = 0
        self.server = gtk.Entry()
        self.server.set_text('http://localhost:8069/xmlrpc')
        self.database = gtk.Entry()
        self.database.set_text('doc')
        self.login = gtk.Entry()
        self.login.set_text('admin')
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        
        col = 0
        for widget in [
            gtk.Label('Server URL: '), self.server,
            gtk.Label('Database: '), self.database,
            gtk.Label('Login: '), self.login,
            gtk.Label('Password: '), self.password,
        ]:
            table.attach(widget, col, col+1, row, row+1, yoptions=False, xoptions=gtk.FILL, ypadding=2)
            col += 1
            if col>1:
                col=0
                row+=1


        self.dia.vbox.pack_start(table, expand=True, fill=True)
        self.dia.show_all()

    def run(self):
        while True:
            res = self.dia.run()
            if res==gtk.RESPONSE_OK:
                _url = self.server.get_text() + '/common'
                sock = xmlrpclib.ServerProxy(_url)
                try:
                    db = self.database.get_text()
                    pa = self.password.get_text()
                    uid = sock.login(db, self.login.get_text(), pa)
                    return uid, db, pa, self.server.get_text()
                except Exception, e:
                    warning('Unable to connect to the server')
                    continue
            self.destroy()
            break
        return False

    def destroy(self):
        self.dia.destroy()

class window2(object):
    def __init__(self, views):
        self.dia = gtk.Dialog(
            'Open ERP View',
            None,
            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT
        )
        self.dia.set_property('default-width', 760)
        self.dia.set_property('default-height', 500)
        self.but_cancel = self.dia.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.views = views
        self.treeview = gtk.TreeView()
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View Name', cell, text=0)
        tvcolumn.set_sort_column_id(0)
        self.treeview.append_column(tvcolumn)
        cell1 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('Object', cell1, text=1)
        tvcolumn.set_sort_column_id(1)
        self.treeview.append_column(tvcolumn)
        cell2 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View Type', cell2, text=2)
        tvcolumn.set_sort_column_id(2)
        self.treeview.append_column(tvcolumn)
        cell3 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View ID', cell3, text=3)
        tvcolumn.set_sort_column_id(3)
        self.treeview.append_column(tvcolumn)
        views.sort()
        views.sort()
        self.liststore = gtk.ListStore(str,str,str, int)
        for v in views:
            self.liststore.append(v)
        self.treeview.set_model(self.liststore)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        sw.set_shadow_type(gtk.SHADOW_NONE)
        sw.add(self.treeview)

        self.dia.vbox.pack_start(sw, expand=True, fill=True)
        self.dia.show_all()

    def run(self):
        while True:
            res = self.dia.run()
            if res==gtk.RESPONSE_OK:
                selection = self.treeview.get_selection()
                model,iter = selection.get_selected_rows()
                if iter:
                    iter = model.get_iter(iter[0])
                    res = model.get_value(iter,3)
                    res2 = model.get_value(iter,1)
                    res3 = model.get_value(iter,2)
                    self.destroy()
                    return res2, res, res3
                else:
                    warning('You must select a ressource !')
                    continue
            self.destroy()
            break
        return False

    def destroy(self):
        self.dia.destroy()


# self.sizes: a stack of containers (forms, groups, notebook, ...)
#   0- number of columns
#   1- total width of the upcomming element in group.notebook etc
#   2- x position (in pixels)
#   3- y position (in height pixels)
#   4- max Y (in pixels)
class display(object):
    def __init__(self, view, default):
        self.view = view
        self.etree = etree.fromstring(view['arch'])
        self.select1 = self.select2 = []
        self.sizes = [[4 ,48 , 0 , 6, 8]]
        self.defaults = default
        self.shapes = {
            'form' : 'shape - head_title',
            'one2many_list': 'shape - one2many',
            'tree' : 'shape - tree_title',
            'label': 'Standard - Text',
        }
        self.attrs = {
            'form': {'group': True, 'label': False, 'colspan':4, 'height': 4},
            'tree': {'colspan':4},
            'group': {'group': True, 'display':False, 'label':False, 'height': 0},
            'notebook': {'group': True, 'display':False, 'label':False, 'height': 0, 'colspan':4},
            'page': {'group': True, 'label':False, 'height': 2, 'colspan':4},
        }
        self.fields = {
            'text': {'height': 4, 'style':{'text_alignment': 2}},
            'text_wiki': {'height': 4, 'style':{'text_alignment': 2}},
            'text_tag': {'height': 4, 'style':{'text_alignment': 2}},
            'one2many': {'height': 10, 'style':{'text_alignment': 0, 'text_font' : 'Helvetica-Bold'}}, # text_font attrib is raising error
            'many2many': {'height': 10, 'style':{'text_alignment': 0}},
            'one2many_form': {'height': 10, 'style':{'text_alignment': 0}},
            'one2many_list': {'height': 10, 'style':{'text_alignment': 0}},
        }

    def draw_element(self, x,y, sizex, sizey, shape, properties, default = None):
        shape = {
            'shape - page': 'shape - notebook_path'
        }.get(shape, shape)
        if type(default) == type(1) and shape == 'shape - boolean':
            shape = 'shape - boolean_on'
        if shape:
            oType = dia.get_object_type (shape)
            o, h1, h2 = oType.create(0,0)
            if ('elem_width'  and 'elem_height' ) in o.properties.keys():
                o.properties['elem_width'] = sizex
                o.properties['elem_height'] = sizey
            for k,v in properties.items():
                    o.properties[k] = v
            o.move(x,y)
            self.data.active_layer.add_object(o)
            
        if default and type(default) != type(1):
            oType = dia.get_object_type ('Standard - Text')
            o, h1, h2 = oType.create(x+0.25,y+1.25)
            o.properties['text'] = str(default)
            self.data.active_layer.add_object(o)
            
    def process_node(self, element, posx=0, posy=0):
        label = element.attrib.get('string','')
        default = None
        colspan = int(element.attrib.get('colspan',self.attrs.get(element.tag, {}).get('colspan', 1)))
        labelspan = 0
        attrs = {
            'text_alignment': 0,
            'text_colour': "#000000",
            'text_height': 1
        }
        height = self.attrs.get(element.tag, {}).get('height', 2)
        if element.tag=='newline':
           return 0, self.sizes[-1][-1]
        if element.tag=='button':
             attrs['text_alignment'] = 1
        if element.tag=='field':
            field_name = element.attrib.get('name')
            attr = self.view['fields'][field_name]
            attr.update(element.attrib)
            if attr.get('required',0):
                attrs['fill_colour'] = "#DDDDFF"
            if attr.get('readonly',0):
                attrs['fill_colour'] = "#EEEEEE"

            nolabel = int(attr.get('nolabel',0))
            if not nolabel:
                posx+=1
                labelspan = 1
                if attr.get('colspan', 0):
                    colspan = int(attr.get('colspan', 0)) - 1
            if not label:
                label = self.view['fields'][field_name]['string']
            if nolabel:
                label = ""
            if field_name in self.defaults and len(self.defaults):
                default = self.defaults[field_name]
                
            shape_type = self.view['fields'][field_name]['type']
            if shape_type == 'many2one':
                if self.view['fields'][field_name].has_key('widget'):
                    shape_type = self.view['fields'][field_name]['widget']
            shape = self.shapes.get(shape_type,'shape - '+shape_type)
            height = self.fields.get(shape_type, {}).get('height', 2)
            label = label and label + ' : '
            attrs['text_alignment'] =self.fields.get(shape_type, {}).get('style',{}).get('text_alignment',2)
        else:
            attrs['text_alignment'] = 0
            shape = self.shapes.get(element.tag,'shape - '+element.tag)

        attrs['text'] = label
        
        colsize = self.sizes[-1][1] / float(self.sizes[-1][0])
        if colspan == 0:
            colspan = 1
        size = colsize * colspan

        if posx+colspan > self.sizes[-1][0]:
            posx = labelspan
            posy = self.sizes[-1][-1]
        self.sizes[-1][-1] = max(self.sizes[-1][-1], posy + height)

        pos_x = posx * colsize  + self.sizes[-1][2]
        pos_y = posy
        if self.attrs.get(element.tag, {}).get('display', True):
            self.draw_element(pos_x, pos_y, size, height, shape, attrs, default)

        posx += colspan

        if element.tag in self.attrs:
            if self.attrs[element.tag].get('group', False):
                col = int(element.attrib.get('col',4))
                self.sizes.append([col, size, pos_x, pos_y, pos_y+height])
                posx2 = 0
                posy2 = posy + height
                for e in element.getchildren():
                    posx2,posy2 = self.process_node(e, posx2, posy2)
                self.sizes[-2][-1] = max(self.sizes[-2][-1],  self.sizes[-1][-1])
                self.sizes.pop()

        return posx,posy
        
    def process_tree(self, element, posx=0, posy=0):
        label = element.attrib.get('string','')
        attrs = {
            'text_alignment': 0,
            'text_colour': "#000000",
        }
        height = self.attrs.get(element.tag, {}).get('height', 2)
        shape = self.shapes.get(element.tag,'shape - '+element.tag)
        pos_x = posx
        pos_y = posy
        attrs['text'] = label
        if element.tag=='tree':
            attrs['text_colour'] =  "#000000"
            self.draw_element(pos_x, pos_y, self.sizes[-1][1], height, shape, attrs)
            self.draw_element(0, pos_y + height, self.sizes[-1][1], 25, 'shape - list', {})
           
        elif element.tag=='field':
            field_name = element.attrib.get('name')
            label = self.view['fields'][field_name]['string']
            attrs['text_alignment'] = 0
            attrs['text_height'] = 0
            self.draw_element(pos_x, 20, self.sizes[-1][1] , height, None, attrs, label)
            posx = posx + len(label)/2
            
        if element.tag in self.attrs:
            col = int(element.attrib.get('col',4))
            self.sizes.append([col, self.sizes[-1][1], pos_x, pos_y, pos_y+height])
            posx2 = 0
            posy2 = posy + height
            for e in element.getchildren():
                posx2,posy2 = self.process_tree(e, posx2, posy2)
            self.sizes[-2][-1] = max(self.sizes[-2][-1],  self.sizes[-1][-1])
                
        return posx,posy
    
    def draw(self, data, flags, type):
        self.data = data
        self.flags = flags
        self.draw_element(0, 0, 60, 5, 'shape - head_logo', {})
        if type == 'form':
            self.process_node(self.etree, 0, 5)
        if type == 'tree':
            self.process_tree(self.etree, 0, 5)
            
        if 'toolbar' in self.view:
            y = 6
            for data in ('print', 'action', 'relate'):
                if not self.view['toolbar'][data]:
                    continue
                self.draw_element(49, y, 11, 1.8 , 'shape - right_toolbar_header', {
                    'text': data.upper(),
                    'text_alignment': 0,
                    'text_colour': "#FFFFFF",
                })
                y += 2
                for relate in self.view['toolbar'][data] :
                     self.draw_element(49, y, 11, 1.8 , 'shape - right_toolbar_text', {
                        'text': relate['string'],
                        'text_alignment': 0
                     })
                     y += 2

        self.data.active_layer.update_extents()

def main(data=True, flags=True, draw=True):
    win = window()
    result = win.run()
    win.destroy()
    if result:
        uid, db, password, server = result
        _url = server + '/object'
        sock = xmlrpclib.ServerProxy(_url)
        ids = sock.execute(db, uid, password, 'ir.ui.view', 'search', [('inherit_id','=',False),('type','in',('form','tree'))])
        views = sock.execute(db, uid, password, 'ir.ui.view', 'read', ids, ['name','type','model'])
        view_lst = map(lambda x: (x['name'],x['model'],x['type'],x['id']), views)
        win = window2(view_lst)
        result = win.run()
        defaults ={}
        if result:
            model, view_id, view_type = result
            views = sock.execute(db, uid, password, model, 'fields_view_get', view_id, view_type, {}, True)
            fields = views['fields']
            for field in fields:
                default = sock.execute(db, uid, password, model, 'default_get',[field])
                if len(default) and default[field]:
                    if fields[field]['type'] == 'many2one':
                        val = sock.execute(db, uid, password, fields[field]['relation'], 'read', default[field], ['name'])['name']
                        default[field] = val
                    defaults.update(default)
                        
            d = display(views, defaults)
            if draw:
                d.draw(data, flags,views['type'])

if __name__=='__main__':
    main(draw =False)


def main2(data, flags):
    layer = data.active_layer
    oType = dia.get_object_type ("shape - char") 
    o, h1, h2 = oType.create (1.4,7.95)
    layer.add_object(o)

dia.register_callback ("Load Open ERP View", 
                       "<Display>/Tools/Load Open ERP View", 
                       main)


