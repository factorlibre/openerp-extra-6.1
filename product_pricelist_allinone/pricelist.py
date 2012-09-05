# -*- encoding: utf-8 -*-

from osv import fields, osv

class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"

    _columns = {
#        "pricelist_version_idid": fields.related(
#                    "price_version_id",
#                    type="many2one",
#                    relation="product.pricelist.version",
#                    store=True,
#                    string="Version List ID"),
        "price_version_name": fields.related(
                    "price_version_id", "name",
                    type="char", readonly=True, size=64,
                    store=True,
                    string="Version Name"),
        "price_version_date_start": fields.related(
                    "price_version_id", "date_start",
                    type="date", readonly=True,
                    store=True,
                    string="Version Start"),
        "price_version_date_end": fields.related(
                    "price_version_id", "date_end",
                    type="date", readonly=True,
                    store=True,
                    string="Version End"),
        "price_version_active": fields.related(
                    "price_version_id", "active",
                    type="boolean", readonly=True,
                    string="Version Active"),
#        "pricelist_idid": fields.related(
#                    "price_version_id", "pricelist_id", "id",
#                    type="integer", readonly=True,
#                    relation="product.pricelist",
#                    store=True,
#                    string="List ID"),
        "pricelist_name": fields.related(
                    "price_version_id", "pricelist_id", "name",
                    type="char", readonly=True, size=64,
                    store=True,
                    string="List Name"),
        "pricelist_type": fields.related(
                    "price_version_id", "pricelist_id", "type",
                    type="char", readonly=True, size=64,
                    store=True,
                    string="List Type"),
        "pricelist_cur": fields.related(
                    "price_version_id", "pricelist_id", "currency_id",
                    type="many2one", readonly=True,
                    relation="res.currency",
                    store=True,
                    string="List Currency"),
        "pricelist_company": fields.related(
                    "price_version_id", "pricelist_id", "company_id",
                    type="many2one", readonly=True,
                    relation="res.company",
                    store=True,
                    string="List Company"),
        }

product_pricelist_item()
