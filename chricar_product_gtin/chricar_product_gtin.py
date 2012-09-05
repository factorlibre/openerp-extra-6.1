# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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

import netsvc
from osv import fields, osv
import math

def is_pair(x):
    return not x%2

def check_ean(eancode):
    if not eancode:
        return True
    if not len(eancode) in [8,12,13,14]:
        return False
    try:
        int(eancode)
    except:
        return False
    sum=0
    ean_len=len(eancode)
    for i in range(ean_len-1):
        pos=int(ean_len-2-i)
        if is_pair(i):
            sum += 3 * int(eancode[pos])
        else:
            sum += int(eancode[pos])
        check = int(math.ceil(sum / 10.0) * 10 - sum)

	i += 1
    if check != int(eancode[ean_len-1]): # last digit
        return False
    return True

class product_product(osv.osv):
    _inherit = "product.product"


    # this def shouldn't be necessary, but is not available from product_product
    def _check_ean_key(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
           res = check_ean(product.ean13)
        return res

    _columns = {
        'ean13': fields.char('EAN', help ='Barcode number for EAN8 EAN13 UPC JPC GTIN http://de.wikipedia.org/wiki/Global_Trade_Item_Number', size=14),
	}

    # this constraint is ADDED, so we have 2 constraints with name _check_ean_key 
    _constraints = [(_check_ean_key, 'Error: Invalid Bar Code Number', ['ean13'])]

product_product()


# ******* Just to be complete ****
# the ean13 is defined in partner.py but apparently not used in any xml
class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'ean13':    fields.char('EAN', help ='Barcode number for EAN8 EAN13 UPC JPC GTIN', size=14),
	}

    def _check_ean_key(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            res = check_ean(product.ean13)
            return res
    _constraints = [(_check_ean_key, 'Error: Invalid Bar Code Number', ['ean13'])]
res_partner()


