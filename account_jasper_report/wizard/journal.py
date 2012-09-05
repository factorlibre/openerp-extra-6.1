import wizard

view_form_start = """<?xml version="1.0"?>
    <form string="Print Journal">
        <image name="gtk-info" size="64" colspan="2"/>
        <group colspan="2" col="4">
            <field name="type" colspan="4"/>
            <field name="order" colspan="4"/>
            <field name="start_date"/>
            <field name="end_date"/>
            <field name="periods" colspan="4"/>
            <field name="journals" colspan="4"/>
        </group>
    </form>"""

view_fields_start = {
    'type': {
        'string': 'Report', 
        'type': 'selection', 
        'selection': [('journal','Journal')], 
        'default': lambda *a: 'journal', 
        'required': True 
    },
    'order': {
        'string': 'Order By', 
        'type': 'selection', 
        'selection': [
            ('number','Move Number'),
            ('date','Move Date'),
        ], 
        'default': lambda *a: 'number', 
        'required': True 
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
    'journals': { 
        'string': 'Journals', 
        'type': 'many2many', 
        'relation': 'account.journal' 
    }
}

class account_report_journal(wizard.interface):
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
                'state':'end',
            }
        }
    }
account_report_journal('account_report_journal')

