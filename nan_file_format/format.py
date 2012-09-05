# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2010   Àngel Àlvarez 
#                      NaN Projectes de programari lliure S.L.
#                      (http://www.nan-tic.com) All Rights Reserved.
#
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


from osv import fields,osv
import os
import unicodedata
from tools.translate import _
import netsvc


def unaccent(text):
    if isinstance( text, str ):
        text = unicode( text, 'utf-8' )
    elif isinstance(text, unicode):
        pass
    else:
        return str(text)
    return unicodedata.normalize('NFKD', text ).encode('ASCII', 'ignore')

class file_format( osv.osv ):
    
    _name = 'file.format'
    _columns = { 
		'name': fields.char('Name', size=30, select=1 , help="Format name" ),
		'path': fields.char('Path', size=300, help="The path to the file name. The last slash is not necessary" ),
		'file_name': fields.char( 'File Name',size=100 , help="File name" ),
		'header': fields.boolean('Header' , help="Header (fields name) on files" ),
		'separator': fields.char( 'Separator',size=1, help="Put here, if it's necessary, the seprator between each field" ),
		'quote': fields.char( 'Quote' ,size=1 ,help="Character to use as quote" ),
		'field_ids': fields.one2many('file.format.field','format_id','Fields' ),
		'model_id': fields.many2one( 'ir.model','Model' ),
	}
    _defaults = {
        'quote': lambda *a: '',
        'separator': lambda *a: '',
    }

    def export_file( self, cr,uid, id, model_ids, context ):
        if not id:
            return False
        format = self.browse( cr, uid, id, context )
        objects = self.pool.get( format.model_id.model ).browse( cr, uid, model_ids, context ) 
        logger = netsvc.Logger()

        header_line = []
        lines=[]
        for object in objects:
            fields = []
            headers = []
            for field in format.field_ids:
                try:
                    field_eval =  eval( field.expression.replace( '$', 'object.' ) )
                except:
                    field_eval=''

                logger.notifyChannel( 'FILE FORMAT', netsvc.LOG_INFO, _( "The expression to export for the %s file is %s and it's val: %s" ) % ( format.name, field.expression, field_eval ) )

                if ( isinstance( field_eval, int ) or isinstance( field_eval, float ) ):
                    if field.format_number:
                        field_eval = field.format_number%field_eval
                    field_eval = str( field_eval ).replace( '.', unaccent( field.decimal_character ) or '' )

                ffield = unaccent( field_eval )
                # If the length of the field is 0, it's means that dosen't matter how many chars it take
                if field.length != 0:
                    #If fill_char field not exists raise WARNING
                    if field.fill_char:
                        if field.align == 'right' :
                            ffield = ffield.rjust( field.length, unaccent( field.fill_char ) )
                        else:
                            ffield = ffield.ljust( field.length, unaccent( field.fill_char ) )
                    else:
                        logger.notifyChannel( 'FILE FORMAT', netsvc.LOG_WARNING, _( "The field 'Fill Char' of the %s is required, because you have selected and specific length" ) % field.name )
                        return False

                    ffield = ffield[ :field.length ]

                field_header = unaccent( field.name )
                if format.quote:
                    if format.quote == '"':
                        ffield = ffield.replace( '"', "'" )
                    elif format.quote == "'":
                        ffield = ffield.replace( "'", '"' )
                    ffield = format.quote + ffield + format.quote
                    field_header = format.quote + field_header + format.quote
                fields.append( ffield )
                headers.append( field_header )
            separator = format.separator or ''
            lines.append( separator.join( fields ) )
            if not header_line:
                header_line.append( separator.join( headers ) )

        try:
            file_path = format.path + "/" + format.file_name
            # Control if we need the headers + if the path file dosen't exists and is a file. To add the headers or not
            if format.header and not os.path.isfile( file_path ):
                # Write the headers in the file
                file = open( file_path, 'w' )
                for header in header_line:
                    file.write( header + "\r\n" )
                file.close()
    
            # Put the information in the file
            file = open( file_path, 'a+' ) 
            for line in lines:
                file.write( line + "\r\n" )
            file.close()
            logger.notifyChannel( 'FILE FORMAT', netsvc.LOG_INFO, _( "the file %s is write correctly" ) % format.file_name )
        except:
            pass

file_format()

class file_format_field( osv.osv ):
    _name = 'file.format.field'
    _rec_name = 'sequence'
    _order = 'sequence asc'
    _columns = {
		'sequence': fields.integer( 'Sequence', help="Is the order that you want for the columns field in the file" ),
		'name': fields.char( 'Name',size=30, select=1, required=True, help="The name of the field. It's used if you have selected the Header checkbox" ),
		'length': fields.integer( 'Length', help="If the length of the field is 0, it's means that dosen't matter how many chars it take" ),
		'fill_char': fields.char( 'Fill Char',size=1, help="If you have writte a specific length, here you have to specify with which char the program have to fill the empty chars" ),
        'format_number': fields.char( 'Number Format', size=10, help="This field is only for the format of an integer or a float. E.g. if you have a float and want 2 decimals you have to write '%.2f' (without simple quotes)" ),
		'expression': fields.text( 'Expression', help="Where we put the python code. The fields are called like '$name_of_field' (without the simple quotes)" ),
		'format_id': fields.many2one( 'file.format','Format' ),
        'align' : fields.selection( [ ('left','Left'),('right','Right') ] , 'Align', help="If you have writte a specific length, you can decid the alignement of the value" ),
        'decimal_character': fields.char( 'Decimal Character', size=1, help="IF you neeed and specific decimal charcter for the float fields" ),
    }
    _defaults = {
        'sequence': lambda *a: 1,
        'fill_char': lambda *a:'',
        'align' : lambda *a: 'left',
    }

    _order = 'sequence'

file_format_field()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
