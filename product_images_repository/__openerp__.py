# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
{
    'name' : 'product_images_repository',
    'version' : '1.0',
    'depends' : ['base', 'product', 'product_images_olbs'],
    'author' : 'Camptocamp',
    "category" : "Added functionality - Product Extension",
    'description': """Add a repository functionnality to the product's images :
 - Images repository: configure a path where all your files are stored on the OpenERP Server thereby you just have to type the name (instead of the full path) of the image file in the image's link field and OpenERP will automatically get the image in the right folder.
 - Wizard to simply add or modify images (upload the image in the repository and create it with the right link on the product)
 - Allow to add other types of files than images (*.jpg, *.gif, *.png) like flash, pdf... They are simply not displayed on the thumbnail. (Preparation for a future module which allow to send these files with ftp/sftp on Magento as images stay exported with MagentoERPconnect)

Configure the "Images Repository Path" on the company, that is the folder where all your images will be stored.
The images stored in the repository must be of type "link" and the filename must only contains the name of the file.
OpenERP will search for them in the configured path.
You can use the wizard "Load an image" on the products to copy the image directly in the repository.
""",
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': [
                   'company_view.xml', 
                   'wizard/load_product_media_view.xml',
                   'product_image_view.xml',
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
