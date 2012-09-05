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

import base64

__description__ = """This plugin generate URL
    url: which defines url
    text_display: defines the text which one want to display on url 
    one can add more arguments which one wants to add as key=value pair in url
"""

__args__ = [('url','string'),('text_display','string')]

def php_url(cr, uid, **plugin_args):
    res =[]
    arguments = ''
    arg = ('url','text_display','encode')
    url_arg = filter(lambda x: x not in arg, plugin_args)
    for a in url_arg:
        if arguments =='':
            arguments  += '%s=%s'%(a, plugin_args[a])
        else:
            arguments  += '&%s=%s'%(a, plugin_args[a])
    if 'encode' in plugin_args and plugin_args['encode']: 
        arguments = base64.encodestring(arguments)
    url_name = plugin_args['url'] or ''
    if url_name and url_name.find('http://')<0 :
        url_name = 'http://' + url_name
        if arguments :
            url_name = url_name+"?data="+ arguments
    value = "<a href= '%s' target='_blank'> %s </a>"%(url_name or '',plugin_args['text_display'] or '')
    return value
#    return (url_name,plugin_args['text_display'])

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
