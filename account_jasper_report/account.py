from osv import osv

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _query_get(self, cr, uid, obj='l', context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        if not context.get('fiscalyear', False):
            fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
            fiscalyear_clause = (','.join([str(x) for x in fiscalyear_ids])) or '0'
        else:
            fiscalyear_clause = '%s' % context['fiscalyear']
        state=context.get('state',False)
        where_move_state = ''
        where_move_lines_by_date = ''

        if context.get('date_from', False) and context.get('date_to', False):
            where_move_lines_by_date = " AND " +obj+".move_id in ( select id from account_move  where date >= '" +context['date_from']+"' AND date <= '"+context['date_to']+"')"
            
        if state:
            if state.lower() not in ['all']:
                where_move_state= " AND "+obj+".move_id in (select id from account_move where account_move.state = '"+state+"')"
        
        date_clause = ''
        if 'start_date' in context:
            date_clause += " AND %s.date >= '%s'" % (obj, context['start_date'])
        if 'end_date' in context:
            date_clause += " AND %s.date <= '%s'" % (obj, context['end_date'])
                
        if context.get('periods', False):
            ids = ','.join([str(x) for x in context['periods']])
            return obj+".state<>'draft' AND "+obj+".period_id in (SELECT id from account_period WHERE fiscalyear_id in (%s) AND id in (%s)) %s %s %s" % (fiscalyear_clause, ids,where_move_state,where_move_lines_by_date, date_clause)
        else:
            return obj+".state<>'draft' AND "+obj+".period_id in (SELECT id from account_period WHERE fiscalyear_id in (%s)) %s %s %s" % (fiscalyear_clause,where_move_state,where_move_lines_by_date, date_clause)

account_move_line()
