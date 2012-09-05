import pooler
import jasper_reports
from datetime import datetime
from tools.translate import _


def parser( cr, uid, ids, data, context ):
    # Process filters from wizard 
    report_type = data['form']['type']
    start_date = data['form']['start_date']
    end_date = data['form']['end_date']
    accounts = data['form'].get('accounts', [])
    if accounts:
        accounts = accounts[0][2]
    else:
        accounts = []
    journals = data['form'].get('journals', [])
    if journals:
        journals = journals[0][2]
    else:
        journals = []
    periods = data['form'].get('periods', [])
    if periods:
        periods = periods[0][2]
    else:
        periods = []
    start_account = data['form'].get('start_account')
    depth = data['form'].get('depth', 0)
    show_balance_zero = data['form'].get('show_balance_zero', False)
    partner_type = data['form'].get('partner_type')
    fiscal_year = data['form'].get('fiscal_year')
    accumulated_periods = data['form'].get('accumulated_periods')
    if accumulated_periods:
        accumulated_periods = accumulated_periods[0][2]
    else:
        accumulated_periods = []

    order = data['form'].get('order')

    pool = pooler.get_pool(cr.dbname)

    # SUBTITLE Parameters
    subtitle = {}
    if start_date:
        subtitle['start_date'] = datetime.strptime( start_date, '%Y-%m-%d' ).strftime( '%d/%m/%Y' )
    else:
        subtitle['start_date'] = '*'
    if end_date:
        subtitle['end_date'] = datetime.strptime( end_date, '%Y-%m-%d' ).strftime( '%d/%m/%Y' )
    else:
        subtitle['end_date'] = '*'

    if journals:
        subtitle['journals'] = ''
        js = pool.get('account.journal').search(cr, uid, [('id','in',journals)], context=context)
        
        journals_subtitle = []
        for x in pool.get('account.journal').read(cr, uid, js, ['name'], context):
            journals_subtitle.append( x['name'] )
        subtitle['journals'] = ','.join( journals_subtitle )
    else:
        subtitle['journals'] = _('ALL JOURNALS')

    if periods:
        subtitle['periods'] = []
        js = pool.get('account.period').search(cr, uid, [('id','in',periods)], order='date_start ASC, date_stop ASC', context=context)
        periods_subtitle = []
        for x in pool.get('account.period').browse(cr, uid, js, context):
            periods_subtitle.append( x.name )
        subtitle['periods'] = ', '.join( periods_subtitle )
        #last_period_id = False
        #for period in pool.get('account.period').browse(cr, uid, js, context):
        #    if not last_period_id or last_period_id != period.id - 1:
        #        sd = datetime.strptime( period.date_start, '%Y-%m-%d' ).strftime('%d/%m/%Y')
        #        ed = datetime.strptime( period.date_stop, '%Y-%m-%d' ).strftime('%d/%m/%Y')
        #        subtitle['periods'].append( ( sd, ed ) )
        #subtitle['periods'] = '%s - %s' % (subtitle['periods'][0][0], subtitle['periods'][-1][1])
    else:
        subtitle['periods'] = _('ALL PERIODS')

    if accounts:
        js = pool.get('account.account').search(cr, uid, [('id','in',accounts)], context=context)
        accounts_subtitle = []
        for x in pool.get('account.account').browse(cr, uid, js, context):
            if len(accounts_subtitle) > 4:
                accounts_subtitle.append( '...' )
                break
            accounts_subtitle.append( x.code ) 
        subtitle['accounts'] = ', '.join( accounts_subtitle )
    else:
        subtitle['accounts'] = _('ALL ACCOUNTS')


    ids = []
    name = ''
    model = ''
    records = []
    data_source = 'model'
    parameters = {}
    if report_type == 'journal':

        s = ''
        s += _('Dates: %s - %s') % (subtitle['start_date'], subtitle['end_date'])
        s += '\n'
        s += _('Journals: %s') % subtitle['journals']
        s += '\n'
        s += _('Periods: %s') % subtitle['periods']
        parameters['SUBTITLE'] = s

        if start_date:
            start_date = "aml.date >= '%s' AND" % str(start_date)
        else:
            start_date = ''
        if end_date:
            end_date = "aml.date <= '%s' AND" % str(end_date)
        else:
            end_date = ''
        if journals:
            journals = ','.join( [str(x) for x in journals] )
            journals = 'aml.journal_id IN (%s) AND' % journals
        else:
            journals = ''
        if periods:
            periods = ','.join( [str(x) for x in periods] )
            periods = 'aml.period_id IN (%s) AND' % periods
        else:
            periods = ''
        
        if order == 'number':
            order_by = 'am.name, aml.date'
        else:
            order_by = 'aml.date, am.name'

        cr.execute("""
            SELECT 
                aml.id 
            FROM 
                account_move am, 
                account_move_line aml 
            WHERE 
                %s
                %s 
                %s
                %s
                am.id=aml.move_id
            ORDER BY 
                %s
        """ % (
            journals,
            periods,    
            start_date,
            end_date,
            order_by,
        ) )
        ids = [x[0] for x in cr.fetchall()]
        name = 'report.account.journal'
        model = 'account.move.line'
        data_source = 'model'

    elif report_type == 'general-ledger':
        s = ''
        s += _('Dates: %s - %s') % (subtitle['start_date'], subtitle['end_date'])
        s += '\n'
        s += _('Journals: %s') % subtitle['journals']
        s += '\n'
        s += _('Accounts: %s') % subtitle['accounts']
        parameters['SUBTITLE'] = s

        domain = []
        fy_periods = []

        if accounts:
            accounts = [('account_id','in',accounts)]
            domain += accounts
        if periods:
            domain += [('period_id','in',periods)]
            for p in pool.get('account.period').browse(cr, uid, periods, context):
                for pp in p.fiscalyear_id.period_ids:
                    fy_periods.append( pp.id )
            
        if start_date:
            domain += [('date','>=',start_date)]
        if end_date:
            domain += [('date','<=',end_date)]
        visibleIds = pool.get('account.move.line').search(cr, uid, domain, context=context)
        lineDomain = accounts
        if fy_periods:
            lineDomain += [('period_id','in',fy_periods)]
        lineIds = pool.get('account.move.line').search(cr, uid, lineDomain, order='account_id, date, name', context=context)

        if order == 'number':
            order_by = 'am.name, aml.date'
        else:
            order_by = 'aml.date, am.name'

        cr.execute("""
            SELECT
                aml.id
            FROM
                account_move_line aml,
                account_move am
            WHERE
                am.id = aml.move_id AND
                aml.id in (%s)
            ORDER BY
                aml.account_id,
                %s
            """ % (','.join([str(x) for x in lineIds]), order_by) )
        lineIds = [x[0] for x in cr.fetchall()]

        lastAccount = None
        sequence = 0
        for line in pool.get('account.move.line').browse(cr, uid, lineIds, context):
            if lastAccount != line.account_id.id:
                lastAccount = line.account_id.id
                balance = 0.0
            balance += line.debit - line.credit
            if line.id in visibleIds:
                if line.partner_id:
                    partner_name = line.partner_id.name
                else:
                    partner_name = ''
                sequence += 1
                records.append({
                    'sequence': sequence,
                    'account_code': line.account_id.code,
                    'account_name': line.account_id.name,
                    'date': line.date + ' 00:00:00',
                    'move_line_name': line.name,
                    'ref': line.ref,
                    'move_name': line.move_id.name,
                    'partner_name': partner_name,
                    'credit': line.credit,
                    'debit': line.debit,
                    'balance': balance
                })
        name = 'report.account.general.ledger'
        model = 'account.move.line'
        data_source = 'records'
    elif report_type == 'trial-balance':
        s = ''
        s += _('Dates: %s - %s') % (subtitle['start_date'], subtitle['end_date'])
        s += '\n'
        s += _('Periods: %s') % subtitle['periods']
        s += '\n'
        s += _('Accounts: %s') % subtitle['accounts']
        parameters['SUBTITLE'] = s

        if accounts:
            accounts = [('id','in',accounts)]
        else:
            accounts = []
        accounts.append( ('parent_id','!=',False) )
        name = 'report.account.trial.balance'
        model = ''
        data_source = 'records'
        accountIds = pool.get('account.account').search(cr, uid, accounts, order='code', context=context)
        periodContext = context.copy()
        if start_date:
            periodContext['start_date'] = start_date 
        if end_date:
            periodContext['end_date'] = end_date 
        if periods:
            periodContext['periods'] = periods
            fiscal_years = []
            for period in pool.get('account.period').browse(cr, uid, periods, context):
                fiscal_years.append( period.fiscalyear_id.id )
            periodContext['fiscalyear'] = ','.join([str(x) for x in fiscal_years])

        accumulatedContext = context.copy()
        if accumulatedContext:
            accumulatedContext['periods'] = accumulated_periods
            fiscal_years = []
            for period in pool.get('account.period').browse(cr, uid, accumulated_periods, context):
                fiscal_years.append( period.fiscalyear_id.id )
            accumulatedContext['fiscalyear'] = ','.join([str(x) for x in fiscal_years])

        accumulated_records = pool.get('account.account').read(cr, uid, accountIds, ['credit','debit','balance'], accumulatedContext)
        accumulated_dict = dict([(x['id'], x) for x in accumulated_records])

        for account in pool.get('account.account').browse(cr, uid, accountIds, periodContext):
            # Only print accounts that have moves.
            if not account.debit and not account.credit:
                continue
            accumulated_values = accumulated_dict[account.id]
            record = {
                'code': account.code,
                'name': account.name,
                'type': account.type, # Useful for the report designer so accounts of type 'view' may be discarded in aggregation.
                'period_credit': account.credit,
                'period_debit': account.debit,
                'period_balance': account.balance,
                'credit': accumulated_values['credit'],
                'debit': accumulated_values['debit'],
                'balance': accumulated_values['balance'],
            }
            records.append( record )
    elif report_type == 'taxes-by-invoice':
        s = ''
        s += _('Dates: %s - %s') % (subtitle['start_date'], subtitle['end_date'])
        s += '\n'
        s += _('Periods: %s') % subtitle['periods']
        parameters['SUBTITLE'] = s

        name = 'report.account.taxes.by.invoice'
        model = 'account.invoice'

        domain = []
        if start_date:
            domain += [('date_invoice','>=',start_date)]
        if end_date:
            domain += [('date_invoice','<=',end_date)]

        if periods:
            domain += [('period_id','in',periods)]

        if partner_type == 'customers':
            domain += [('type','in',('out_invoice','out_refund'))]
        else:
            domain += [('type','in',('in_invoice','in_refund'))]

        ids = pool.get('account.invoice').search(cr, uid, domain, context=context)


    return { 
        'ids': ids, 
        'name': name, 
        'model': model, 
        'records': records, 
        'data_source': data_source,
        'parameters': parameters,
    }

jasper_reports.report_jasper( 'report.account.journal', 'account.move.line', parser )
jasper_reports.report_jasper( 'report.account.trial.balance', 'account.account', parser )
jasper_reports.report_jasper( 'report.account.general.ledger', 'account.move.line', parser )
jasper_reports.report_jasper( 'report.account.taxes.by.invoice', 'account.invoice', parser )

