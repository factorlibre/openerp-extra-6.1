import wizard
import pooler

view_form_start = """<?xml version="1.0"?>
    <form string="Print General Ledger">
        <image name="gtk-info" size="64" colspan="2"/>
        <group colspan="2" col="4">
            <field name="type" colspan="4"/>
            <field name="order" colspan="4"/>
            <field name="start_date"/>
            <field name="end_date"/>
            <field name="periods" colspan="4"/>
            <field name="accounts" colspan="4"/>
        </group>
    </form>"""

view_fields_start = {
    'type': {
        'string': 'Report', 
        'type': 'selection', 
        'selection': [('general-ledger','General Ledger')], 
        'default': lambda *a: 'general-ledger', 
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
        'string': 'Start Date', 
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
    'accounts': {
        'string': 'Accounts',
        'type': 'many2many',
        'relation': 'account.account'
    },
}


class account_report_general_ledger(wizard.interface):

    def _before(self, cr, uid, data, context):
        if data.get('model','') != 'res.partner':
            return {}
        pool = pooler.get_pool(cr.dbname)
        ids = []
        for partner in pool.get('res.partner').browse(cr,uid,data['ids']):
            if partner.property_account_payable:
                ids.append( partner.property_account_payable.id )
            if partner.property_account_receivable:
                ids.append( partner.property_account_receivable.id )
        return { 'accounts': ids }

    states = {
        'init': {
            'actions': [_before],
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
                'report': 'account.general.ledger', 
                'state':'end'
            }
        }
    }
account_report_general_ledger('account_report_general_ledger')

