import wizard

view_form_start = """<?xml version="1.0"?>
	<form string="Print Journal">
		<image name="gtk-info" size="64" colspan="2"/>
		<group colspan="2" col="4">
			<field name="type" colspan="4"/>
			<field name="start_date"/>
			<field name="end_date"/>
			<field name="accounts" colspan="4"/>
			<field name="periods" colspan="4"/>
			<field name="accumulated_periods" colspan="4"/>
		</group>
	</form>"""

view_fields_start = {
	'type': {
        'string': 'Report', 
        'type': 'selection', 
        'selection': [('trial-balance','Trial Balance')], 
        'default': lambda *a: 'trial-balance', 
        'required': True 
    },
	'start_date': {
        'string': 'Start Date', 
        'type':'date', 
    },
	'end_date': {
        'string': 'End Date',
        'type':'date', 
    },
	'periods': {
        'string': 'Periods',
        'type': 'many2many',
        'relation': 'account.period'
    },
	'accounts': {
        'string': 'Accounts', 
        'type': 'many2many', 
        'relation': 'account.account' 
    },
	'accumulated_periods': {
        'string': 'Accumultated Periods', 
        'type': 'many2many', 
        'relation': 'account.period' 
    },
}


class account_report_trial_balance(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {
				'type': 'form', 
				'arch': view_form_start, 
				'fields': view_fields_start, 
				'state': [('end','Cancel','gtk-cancel'),('print','Print','gtk-ok')]
			}
		},
		'print': {
			'actions': [],
			'result': {
				'type': 'print', 
				'report': 'account.trial.balance', 
				'state':'end'
			}
		}
	}
account_report_trial_balance('account_report_trial_balance')
