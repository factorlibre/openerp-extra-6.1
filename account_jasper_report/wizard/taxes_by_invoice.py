import wizard

view_form_start = """<?xml version="1.0"?>
	<form string="Taxes by Invoice">
		<image name="gtk-info" size="64" colspan="2"/>
		<group colspan="2" col="4">
			<field name="type" colspan="4"/>
			<field name="partner_type" colspan="4"/>
			<field name="start_date"/>
			<field name="end_date"/>
            <field name="periods" colspan="4"/>
		</group>
	</form>"""

view_fields_start = {
	'type': {
        'string': 'Report', 
        'type': 'selection', 
        'selection': [('taxes-by-invoice','Taxes by Invoice')], 
        'default': lambda *a: 'taxes-by-invoice', 
        'required': True 
    },
	'partner_type': { 
        'string': 'Invoice Type', 
        'type': 'selection', 
        'selection': [('customers','Customers'),('suppliers','Suppliers')], 
        'default': lambda *a: 'customers' 
    },
	'start_date': { 
        'string':'Start Date', 
        'type':'date', 
    },
	'end_date': { 
        'string':'End Date', 
        'type':'date', 
    },
	'periods': {
        'string': 'Periods', 
        'type': 'many2many', 
        'relation': 'account.period'
    },
}


class account_taxes_by_invoice(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {
				'type': 'form', 
				'arch': view_form_start, 
				'fields': view_fields_start, 
				'state': [('end','_Cancel','gtk-cancel'),('print','_Print','gtk-ok')]
			}
		},
		'print': {
			'actions': [],
			'result': {
				'type': 'print', 
				'report': 'account.journal', 
				'state':'end'
			}
		}
	}
account_taxes_by_invoice('account_report_taxes_by_invoice')
