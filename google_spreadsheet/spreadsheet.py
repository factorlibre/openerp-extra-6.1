# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
# Copyright (c) 2011 Cubic ERP - Teradata SAC. (http://cubicerp.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import gdata.spreadsheet.service
from osv import osv, fields
import netsvc

class google_worksheet(osv.osv):
    """
    Google Spreadsheet Worksheet object
    """
    
    _name = 'google.worksheet'
    _description = "Object to manage the Google Worksheet data"
    _rec_name = 'key_title'
    _columns = {
        'key_id':fields.char('Spreadsheet id', 64, required=True, select=1),
        'key_url': fields.char('Spreadsheet URL', 256, required=False),
        'key_title': fields.char('Spreadsheet Title', 512, required=True, select=1),
        'worksheet_id':fields.char('Worksheet id', 8, required=True),
        'worksheet_url': fields.char('Worksheet URL', 256, required=False),
        'worksheet_title': fields.char('Worksheet Title', 512, required=False, select=1),
        'field_ids' : fields.one2many('google.worksheet.columns', 'worksheet_id','Worksheet Fields'),
        'fields_mapping': fields.one2many('google.worksheet.fields.mapping', 'worksheet_id','Fields Mapping'),
        'row_ids': fields.one2many('google.worksheet.rows', 'worksheet_id','Data Preview'),
        'cell_ids': fields.one2many('google.worksheet.cells', 'worksheet_id','Data Preview'),
        'errors': fields.text('Errors'),
        'messages' : fields.text('Messages'),
    }
    _defaults = {
    }
    
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['key_title', 'worksheet_title'], context=context)
        res = []
        for record in reads:
            name = record['key_title']
            if record['worksheet_title']:
                name = name + ' ['+record['worksheet_title'] + ']'
            res.append((record['id'], name))
        return res

    def get_client(self,email,password,context=None):
        client = gdata.spreadsheet.service.SpreadsheetsService()
        client.email = email
        client.password = password
        client.source = 'OpenERP Spreadsheet Module by CubicERP.com'
        try:
            client.ProgrammaticLogin()
        except Exception, e:
            raise osv.except_osv('Error', 'Error at try to connect to Google: %s'%e)
            return False
        if context is None:
            context['gdata_client'] = client
        return client
    
    def get_worksheets(self,cr,uid,client,context=None):
        if context is None: context = {}    
        try:
            for ss in client.GetSpreadsheetsFeed().entry:
                vals = {}
                vals['key_title'] = ss.title.text
                vals['key_url'] = ss.id.text
                key_url_parts = vals['key_url'].split('/')
                vals['key_id'] = key_url_parts[len(key_url_parts) - 1]
                for ws in client.GetWorksheetsFeed(vals['key_id']).entry:
                    vals['worksheet_title'] = ws.title.text
                    vals['worksheet_url'] = ws.id.text
                    worksheet_url_parts = vals['worksheet_url'].split('/')
                    vals['worksheet_id'] = worksheet_url_parts[len(worksheet_url_parts) - 1]
                    ws_ids = self.search(cr,uid,[('key_id','=',vals['key_id']),('worksheet_id','=',vals['worksheet_id'])],context=context)
                    if ws_ids: 
                        self.write(cr,uid,ws_ids,vals,context=context)
                    else:
                        self.create(cr,uid,vals,context=context)
                    
        except Exception, e:
            raise osv.except_osv('Error', 'Error at try to get worksheets: %s'%e)
            return False
            
        return True

google_worksheet()

class google_worksheet_columns(osv.osv):
    ''' Columns '''
    _name = "google.worksheet.columns"
    _columns = {
        'name': fields.char('Name',size=256),
        'column' : fields.char('Column',size=4,required=True),
        'worksheet_id' : fields.many2one('google.worksheet','Worksheet', select=1, ondelete="cascade"),
        'col' : fields.integer('Column Number'),
        'cell_ids': fields.one2many('google.worksheet.cells', 'col_id','Fields Mapping'),
    }
    
    def fill_worksheet_column(self,cr,uid,worksheet_id,cell,context=None):
        if context is None: context = {}
        if self.search(cr,uid,[('worksheet_id','=',worksheet_id),('col','=',cell.cell.col)],context=context): return False
        column = ''
        for c in cell.title.text:
            if c.isdigit(): break
            column += c
        vals = {'name' : cell.content.text,
                'column' : column,
                'worksheet_id' : worksheet_id,
                'col' : cell.cell.col,}
        self.create(cr,uid,vals,context=context)
        return True
    
google_worksheet_columns()

class google_worksheet_fields_mapping(osv.osv):
    ''' Fields Mapping '''
    _name = 'google.worksheet.fields.mapping'
    _columns = {
        'model_field_id' : fields.many2one('ir.model.fields','Campo del Objeto',required=True),
        'worksheet_field_id' : fields.many2one('google.worksheet.columns','Column of Worksheet',required=False),
        'worksheet_id' : fields.many2one('google.worksheet','Worksheet', select=1, ondelete="cascade"),
        'value' : fields.char('String Value',2048,help='The value must be same type of the model field'),
        
        #'model_id': fields.many2one('ir.model', 'Object', required=True, domain=[('osv_memory','=',False)],),
    }
    
    def refresh(self,cr,uid,model_id,worksheet_id,client,context=None):
        obj_column = self.pool.get('google.worksheet.columns')
        obj_model = self.pool.get('ir.model')
        
        if context is None: context = {}
        res = []
        
        #Clean fields mapping
        if_ids = self.search(cr,uid,[('worksheet_id','=',worksheet_id)],context=context)
        if if_ids : self.unlink(cr,uid,if_ids,context=context)
        
        for f in obj_model.browse(cr,uid,model_id,context=context).field_id:
            if f.ttype in ('many2many','one2many','binary','reference','related','function'):
                continue
            
            vals = {'worksheet_id':worksheet_id,'model_field_id':f.id}
            wsc_ids = obj_column.search(cr,uid,[('worksheet_id','=',worksheet_id),('name','ilike','%'+f.name+'%')],context=context)
            if wsc_ids:
                vals['worksheet_field_id'] = wsc_ids[0]
                
            res.append(self.create(cr,uid,vals,context=context))
            
        return res

google_worksheet_fields_mapping()

class google_worksheet_rows(osv.osv):
    ''' Rows '''
    _name = 'google.worksheet.rows'
    _columns = {
        'row' : fields.integer('Row',required=True, select=1),
        'name': fields.char('Name',size=256),
        'content' : fields.text('Row Content',required=False),
        'state' : fields.selection([('draft','Draft'),('error','Error'),('done','Done')],'State'),
        'error' : fields.text('Error Message'),
        'row_id':fields.char('Row id', 8),
        'row_url': fields.char('Row URL', 256, required=False),
        'cell_ids': fields.one2many('google.worksheet.cells', 'row_id','Cells Data'),
        'worksheet_id' : fields.many2one('google.worksheet','Worksheet', select=1, ondelete="cascade"),
        'model_row_id' : fields.integer('ID data', select=1),
    }
    _default = {
        'state' : 'draft',
    }
    
    def fill_rows(self, cr, uid, worksheet_id, client, context=None):
        if context is None: context = {}
        res = {}
        obj_worksheet = self.pool.get('google.worksheet')
        worksheet= obj_worksheet.browse(cr,uid,worksheet_id,context=context)

        #Clean rows data
        if_ids = self.search(cr,uid,[('worksheet_id','=',worksheet_id)],context=context)
        if if_ids : self.unlink(cr,uid,if_ids,context=context)
            
        lf = []
        try:
            lf = client.GetListFeed(worksheet.key_id, worksheet.worksheet_id).entry
        except Exception, e:
            raise osv.except_osv('Error', 'Error at try to get rows: %s'%e)
            return False
        #Generate head
        res['1'] = self.create(cr,uid,{'row':1,'name':'title','worksheet_id':worksheet_id},context=context)
        #Generate body
        for i,l in enumerate(lf):
            vals = {}
            row = i+2
            vals['row'] = row
            vals['name'] = l.title.text
            vals['content'] = l.content.text
            vals['row_url'] = l.id.text
            row_url_parts = vals['row_url'].split('/')
            vals['row_id'] = row_url_parts[len(row_url_parts) - 1]
            #vals['error'] = "%s - %s"%(l.title.text,l.id.text)
            vals['worksheet_id'] = worksheet_id
            res[str(row)] = self.create(cr,uid,vals,context=context)
            
        return res
        
google_worksheet_rows()

class google_worksheet_cells(osv.osv):
    ''' Cells '''
    _name = 'google.worksheet.cells'
    _columns = {
        'row_id' : fields.many2one('google.worksheet.rows','Row',required=True, select=1, ondelete="cascade"),
        'col_id' : fields.many2one('google.worksheet.columns','Column',required=True, select=1, ondelete="cascade"),
        'name' :  fields.char('Name',size=256),
        'content' : fields.text('Cell Content',required=False),
        'cell_id' : fields.char('Cell id', 8, required=True),
        'cell_url' : fields.char('Cell URL', 256, required=False),
        'cell_row' : fields.integer('Row Number'),
        'cell_col' : fields.integer('Column Number'),
        'worksheet_id' : fields.many2one('google.worksheet','Worksheet', select=1, ondelete="cascade"),
        'state' : fields.selection([('draft','Draft'),('error','Error'),('done','Done')],'State'),
        'error' : fields.text('Error'),
    }
    _default = {
        'state' : 'draft',
    }
    
    def fill_cells(self, cr, uid, worksheet_id, client, context=None):
        if context is None: context = {}
        res = []
        obj_fields = self.pool.get('google.worksheet.columns')
        obj_import_data = self.pool.get('google.worksheet.rows')
        obj_worksheet = self.pool.get('google.worksheet')
        worksheet = obj_worksheet.browse(cr,uid,worksheet_id,context=context)

        #Clean cells data
        if_ids = self.search(cr,uid,[('worksheet_id','=',worksheet_id)],context=context)
        if if_ids : self.unlink(cr,uid,if_ids,context=context)
        
        fill_fields = True
        cf = []
        try:
            cf = client.GetCellsFeed(worksheet.key_id, worksheet.worksheet_id).entry
        except Exception, e:
            raise osv.except_osv('Error', 'Error at try to get cells: %s'%e)
            return False
        
        for c in cf:
            #netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "c: %s"%(c))
            if fill_fields: fill_fields = obj_fields.fill_worksheet_column(cr,uid,worksheet_id,c,context=context)
            vals = {}
            import_data_ids = obj_import_data.search(cr,uid,[('worksheet_id','=',worksheet_id),('row','=',c.cell.row)],context=context)
            #netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "import_data_ids:%s - worksheet_id: %s - row: %s"%(import_data_ids,worksheet_id,c.cell.row))
            fields_ids = obj_fields.search(cr,uid,[('worksheet_id','=',worksheet_id),('col','=',c.cell.col)],context=context)
            #netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "fields_ids:%s - worksheet_id: %s - col: %s"%(fields_ids,worksheet_id,c.cell.col))
            vals['worksheet_id'] = worksheet_id
            vals['row_id'] = import_data_ids and import_data_ids[0] or False
            vals['col_id'] = fields_ids and fields_ids[0] or False
            vals['name'] = c.title.text
            vals['content'] = c.content.text
            vals['cell_url'] = c.id.text
            parts = vals['cell_url'].split('/')
            vals['cell_id'] = parts[len(parts) - 1]
            vals['cell_row'] = c.cell.row
            vals['cell_col'] = c.cell.col
            res.append(self.create(cr,uid,vals,context=context))
        return res

    def fill_cells(self, cr, uid, worksheet_id, client, rows_id, context=None):
        if context is None: context = {}
        res = []
        obj_fields = self.pool.get('google.worksheet.columns')
        obj_import_data = self.pool.get('google.worksheet.rows')
        obj_worksheet = self.pool.get('google.worksheet')
        worksheet = obj_worksheet.browse(cr,uid,worksheet_id,context=context)

        #Clean cells data
        netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "worksheet_id: %s"%(worksheet_id))
        if_ids = self.search(cr,uid,[('worksheet_id','=',worksheet_id)],context=context)
        if if_ids : self.unlink(cr,uid,if_ids,context=context)
        
        fill_fields = True
        cf = []
        try:
            cf = client.GetCellsFeed(worksheet.key_id, worksheet.worksheet_id).entry
        except Exception, e:
            raise osv.except_osv('Error', 'Error at try to get cells: %s'%e)
            return False
        
        for c in cf:
            #netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "c: %s"%(c))
            if fill_fields: fill_fields = obj_fields.fill_worksheet_column(cr,uid,worksheet_id,c,context=context)
            vals = {}
            fields_ids = obj_fields.search(cr,uid,[('worksheet_id','=',worksheet_id),('col','=',c.cell.col)],context=context)
            #netsvc.Logger().notifyChannel("fill_cells", netsvc.LOG_INFO, "fields_ids:%s - worksheet_id: %s - col: %s"%(fields_ids,worksheet_id,c.cell.col))
            vals['worksheet_id'] = worksheet_id
            vals['row_id'] = rows_id.get(c.cell.row, False)
            vals['col_id'] = fields_ids and fields_ids[0] or False
            vals['name'] = c.title.text
            vals['content'] = c.content.text
            vals['cell_url'] = c.id.text
            parts = vals['cell_url'].split('/')
            vals['cell_id'] = parts[len(parts) - 1]
            vals['cell_row'] = c.cell.row
            vals['cell_col'] = c.cell.col
            res.append(self.create(cr,uid,vals,context=context))
        return res

    def get_map_value(self, cr, uid, cell_id, mapping_id, context=None):
        if context is None: context = {}
        obj_mapping = self.pool.get('google.worksheet.fields.mapping')
        
        cell = self.browse(cr,uid,cell_id,context=context)
        mapping = obj_mapping.browse(cr,uid,mapping_id,context=context)
        val = cell.content
        try:
            if mapping.model_field_id.ttype in ('float'):
                val = float(val)
            if mapping.model_field_id.ttype in ('boolean'):
                if val.upper() == 'FALSE': val = False
                elif val.upper() == 'TRUE': val = True
                elif val.isdigit(): val = int(val)
                val = bool(val)
            if mapping.model_field_id.ttype in ('integer'):
                val = int(val)
            if mapping.model_field_id.ttype in ('many2one'):
                if val.isdigit():
                    val = int(val)
                else:
                    obj = self.pool.get(mapping.model_field_id.relation)
                    obj_ids = obj.name_search(cr,uid,name=val)
                    if obj_ids:
                        val = obj_ids[0][0]
                    else:
                        netsvc.Logger().notifyChannel("get_map_value", netsvc.LOG_INFO,"cell_id:%s - content: %s - val: %s \n No Values - relation: %s"%(cell_id,cell.content,val,obj_ids,mapping.model_field_id.relation))
                        self.write(cr,uid,cell_id,{'error':'No Values - relation: %s - val: %s'%(mapping.model_field_id.relation,val)},context=context)
                    
                    if len(obj_ids) > 1: 
                        netsvc.Logger().notifyChannel("get_map_value", netsvc.LOG_INFO,"cell_id:%s - content: %s - val: %s \n Multipe Values: %s - relation: %s"%(cell_id,cell.content,val,obj_ids,mapping.model_field_id.relation))
                        self.write(cr,uid,cell_id,{'error':'Multiple Values: %s - relation: %s'%(obj_ids,mapping.model_field_id.relation)},context=context)
                    
        except Exception, e:
            netsvc.Logger().notifyChannel("get_map_value", netsvc.LOG_INFO,'cell_id:%s - name: %s - content: %s - val: %s \n Error: %s'%(cell_id,cell.name,cell.content,val,e))
            raise osv.except_osv('Error','cell_id:%s - name: %s - content: %s - val: %s \n Error: %s'%(cell_id,cell.name,cell.content,val,e))
            self.write(cr,uid,cell_id,{'state':'error','error':e},context=context)
        
        return val
                    
google_worksheet_cells()


class google_worksheet_import_wizard(osv.osv_memory):
    _name = 'google.worksheet.import.wizard'
    _description = "Wizard to import data from a Google Spreadsheet Worksheet"
    _columns = {
        'model_id': fields.many2one('ir.model', 'Object', required=True, domain=[('osv_memory','=',False)],),
        'email': fields.char('Google User',size=128, required=True,),
        'password' : fields.char('Google Password',size=64, required=True),
        'worksheet_id' : fields.many2one('google.worksheet', 'Worksheet', required=True,),
        'partial' : fields.boolean('Import Partial', help="Use this option to add a column ($$_partial_$$) in the worksheet to manage the state of the import by each row"),
        'row_data' : fields.integer('Data Start at Row'),
        
        'import_fields': fields.related('worksheet_id','fields_mapping',type='one2many', relation="google.worksheet.fields.mapping",string="Fields Mapping"),
        'import_data': fields.related('worksheet_id','row_ids',type='one2many', relation='google.worksheet.rows', string='Data Rows'), 
        
        #'errors': fields.related('worksheet_id','errors', type='text', string='Errors', readonly=True),
        #'messages' : fields.related('worksheet_id','messages', type='text',string='Messages', readonly=True),
        'errors': fields.text('Errors'),
        'messages' : fields.text('Messages'),

        'state' : fields.selection([('draft','Draft'),('logged','Logged'),('process','Process'),('done','Done')],'State', readonly=True),
        }
        
    def _get_active_model(self, cr, uid, context=None):
        if not context:
            return False
        else:
            return context.get('active_id')

    _defaults = {
        'model_id': lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('model_id',False) or False,
        'worksheet_id': lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('worksheet_id',False) or False,
        'partial' : True,
        'errors' : lambda *a: '',
        'messages' : lambda *a: '',
        'row_data' : 2,
        'state' : 'draft',
        'email' : lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('email','') or '',
        'password' : lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('password','') or '',
        'errors' : lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('errore','') or '',
        'messages' : lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('messages','') or '',
        #'import_fields': lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('import_fields',False) or False,
        #'import_data': lambda self, cr, uid, context=None: isinstance(context,dict) and context.get('import_data',False) or False,
        
    }
       
    def action_login(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        obj_worksheet = self.pool.get('google.worksheet')
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        client = context.get('gdata_client',False)
        if client:
            if client.email != wizard.email:
                client = obj_worksheet.get_client(wizard.email,wizard.password,context=context)
        else:
            client = obj_worksheet.get_client(wizard.email,wizard.password,context=context)
        
        if not client:
            return False
        context['email'] = wizard.email
        context['password'] = wizard.password
        
        obj_worksheet.get_worksheets(cr,uid, client, context=context)
        
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','worksheet_import_view_wiz_form_2')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'google.worksheet.import.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        
    def action_get_data(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        obj_fields_mapping = self.pool.get('google.worksheet.fields.mapping')
        if context is None:
            context = {}
        
        wizard = self.browse(cr, uid, ids[0], context=context)
        ws_id = wizard.worksheet_id.id
        m_id = wizard.model_id.id
        context['model_id'] = m_id
        context['worksheet_id'] = ws_id
        
        fm_ids = obj_fields_mapping.search(cr,uid,[('worksheet_id','=',ws_id)],context=context)
        if not fm_ids:
            self.action_refresh_fields(cr, uid, ids, context=context)
                
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','worksheet_import_view_wiz_form_3')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'google.worksheet.import.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }        
        
    def action_do_import(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj_model = self.pool.get('ir.model.data')
        obj_worksheet = self.pool.get('google.worksheet')
        obj_mapping = self.pool.get('google.worksheet.fields.mapping')
        obj_cells = self.pool.get('google.worksheet.cells')
        obj_rows = self.pool.get('google.worksheet.rows')
        wizard = self.browse(cr, uid, ids[0], context=context)
        obj = self.pool.get(wizard.model_id.model)
        ws_id = wizard.worksheet_id.id
        rows_created = []
        rows_error = []
        rows_ignored = []
        err = ''
        msg =''
                
        for row in wizard.import_data:
            netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO,"Row:%s (id: %s) \n"%(row.row,row.id))
            if row.row < wizard.row_data:
                rows_ignored.append(row.id)
                msg += "Row:%s (id:%s) Ignored less than %s \n"%(row.row,row.id,wizard.row_data)
                netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO, "Row:%s (id:%s) Ignored less than %s \n"%(row.row,row.id,wizard.row_data))
                continue
            if row.state == 'done':
                rows_ignored.append(row.id)
                msg += "Row:%s (id:%s) Ignored state:%s \n"%(row.row,row.id,row.state)
                netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO,"Row:%s (id:%s) Ignored state:%s \n"%(row.row,row.id,row.state))
                continue
            cell_ids = []
            vals = {}
            for cell in row.cell_ids:
                mapping_ids = obj_mapping.search(cr,uid,[('worksheet_id','=',cell.worksheet_id.id),('worksheet_field_id','=',cell.col_id.id)],context=context)
                if  not mapping_ids : continue
                mapping_id = mapping_ids[0]
                mapping = obj_mapping.browse(cr,uid,mapping_id,context=context)
                cell_id = cell.id

                vals[mapping.model_field_id.name] = obj_cells.get_map_value(cr, uid, cell_id, mapping_id)
                cell_ids.append(cell_id)
            if not vals:
                rows_ignored.append(row.id)
                msg += "Row:%s (id:%s) Ignored there aren't values %s \n"%(row.row,row.id,vals)
                netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO,"Row:%s (id:%s) Ignored there aren't values %s \n"%(row.row,row.id,vals))
                continue
            try:
                obj_id = obj.create(cr,uid,vals,context=context)
                rows_created.append(obj_id)
                msg += "Row:%s (id:%s) Created: %s(id:%s) \n"%(row.row,row.id,wizard.model_id.name,obj_id)
                netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO,"Row:%s (id:%s) Created: %s(id:%s) \n"%(row.row,row.id,wizard.model_id.name,obj_id))
                obj_rows.write(cr,uid,[row.id],{'state':'done','model_row_id':obj_id},context=context)
                obj_cells.write(cr,uid,cell_ids,{'state':'done'},context=context)
                
            except Exception, e:
                netsvc.Logger().notifyChannel("action_do_import", netsvc.LOG_INFO,"Error at create te Row:%s (id:%s) Vals: %s - Error:%s \n"%(row.row,row.id,vals,e))
                raise osv.except_osv('Error','model:%s - row: %s \n vals: %s \n Error: %s'%(wizard.model_id.model,row.row,vals,e))
                err += "Error at create te Row:%s (id:%s) Vals: %s - Error:%s \n"%(row.row,row.id,vals,e)
                rows_error.append(row.id)
                obj_rows.write(cr,uid,[row.id],{'vals: %s \n error':(vals,e),'state':'error'},context=context)
                obj_cells.write(cr,uid,cell_ids,{'state':'error'},context=context)
                
                
        context['errors'] = err
        context['messages'] = msg
        obj_worksheet.write(cr,uid,ws_id,{'messages':msg},context=context)
        obj_worksheet.write(cr,uid,ws_id,{'errors':err},context=context)
        cr.commit()
        raise osv.except_osv('Info', 'Rows: created %s - Errors %s Ignored %s, see the messages page to more information.'%(len(rows_created),len(rows_error),len(rows_ignored)))
        
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','worksheet_import_view_wiz_form_3')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'google.worksheet.import.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }


    def action_refresh_fields(self, cr, uid, ids, context=None):
        ''' Refresh the fields mapping '''
        obj_fields_mapping = self.pool.get('google.worksheet.fields.mapping')
        obj_worksheet = self.pool.get('google.worksheet')
        obj_model = self.pool.get('ir.model.data')
        wizard = self.browse(cr, uid, ids[0], context=context)
        client = context.get('gdata_client',obj_worksheet.get_client(wizard.email,wizard.password,context=context))
        #Need import data to obtain the fields of the worksheet
        if not len(wizard.import_data):
            self.action_refresh_data(cr,uid,ids,context=context)
            
        context['import_fields'] = obj_fields_mapping.refresh(cr,uid,wizard.model_id.id,wizard.worksheet_id.id,client,context=context)
        
        return False
        
        '''model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','worksheet_import_view_wiz_form_3')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'google.worksheet.import.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }'''


    def action_refresh_data(self, cr, uid, ids, context=None):
        obj_import_data = self.pool.get('google.worksheet.rows')
        obj_import_cell = self.pool.get('google.worksheet.cells')
        obj_worksheet = self.pool.get('google.worksheet')
        obj_model = self.pool.get('ir.model.data')

        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        client = context.get('gdata_client',obj_worksheet.get_client(wizard.email,wizard.password,context=context))
        
        rows_id = obj_import_data.fill_rows(cr, uid, wizard.worksheet_id.id, client, context=context)
        obj_import_cell.fill_cells(cr, uid, wizard.worksheet_id.id, client, rows_id,context=context)
        
        context['import_data'] = rows_id.values()
        
        return False
        
        '''model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','worksheet_import_view_wiz_form_3')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'google.worksheet.import.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }'''

        
google_worksheet_import_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
