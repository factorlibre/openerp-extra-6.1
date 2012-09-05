{
    "name": "Alternative Inventory Management",
    "version": "1.0",
    "author": "Tiny",
    "description": """
This module changes the way inventory management is made.


Idea
####

The idea for this module is to set stock quantities only for products listed in
this inventory and only for locations which are defined in this inventory. All
other stock quantities will be set to 0 for every products and every locations
not listed in this inventory.


Products not listed in the inventory
####################################

Products not listed in the inventory have their stock quantities set to 0 to
all their locations.


Locations not listed in the inventory
#####################################

For products listed in the inventory, stock quantities are set to 0 to all
their locations not listed.


Inventory line quantity defaults to 1
#####################################

The default quantity for a line in the original *stock* module is equal to the
stock value for the location specified in this line.

This module sets the default quantity to just 1. This way is more compatible
with barcode scanners where you scan products one by one.



""",
    'category': 'Generic Modules/Inventory Control',
    "depends": ["stock"],
    "init_xml": [],
    "update_xml": [
    ],
    "demo_xml": [],
    "installable": True,
}
