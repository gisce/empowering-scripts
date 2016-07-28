from utils import *

OTS = ['OT101', 'OT103' ,'OT201', 'OT401']

def available(obj, contract_id, period):
    partner_obj = obj['erp'].model('res.partner')
    contract_obj = obj['erp'].model('giscedata.polissa')
    emp_obj = obj['heman']

    contract = contract_obj.read(contract_id, ['name', 'pagador'])
    partner_id = contract['pagador'][0] 
    contract = contract['name']
    if not partner_id:
        return False

    token = partner_obj.read(partner_id, ['empowering_token'])['empowering_token']
    if not token:
        return False
  
    for ot in OTS:
        if not emp_obj.get(contract, token, ot, period):
            return False
    return True

def updated(obj, contract_id):
    contract_obj = obj['erp'].model('giscedata.polissa')
    log_obj = obj['erp'].model('empowering.customize.profile.channel.log')

    last_measure = contract_obj.read(contract_id, ['data_ultima_lectura'])['data_ultima_lectura']
    period = toperiod(todatetime(last_measure, False) - relativedelta(months=1))
    log_ids = log_obj.search([('contract_id', '=', contract_id),
                              ('channel_id', '=', 1),
                              ('sent', '=', True)])
    if not available(obj, contract_id, period):
        return None

    if not log_ids:
        return period

    # TODO: period id utilization instead of last_generated
    last_report = log_obj.read(log_ids[0], ['last_generated'])['last_generated']
    return period \
        if (todatetime(last_measure, False) > todatetime(last_report, True)) else None
  
def pending(obj, contracts):
    contract_obj = obj['erp'].model('giscedata.polissa')

    search_params = [('cups.empowering', '=', True),
                     ('cups.empowering_quarantine', '=', 1)]

    if contracts is not None:
        if not isinstance(contracts, list):
            contracts = [contracts]
        search_params.append(('name', 'in', contracts))
    return [(contract_id, updated(obj, contract_id))
        for contract_id in contract_obj.search(search_params)] 

def deliver(obj, contracts):
    contract_obj = obj['erp'].model('giscedata.polissa')
    groups = zip(*(iter(contracts),)*50)
    for idx,group in enumerate(groups[:1]):
	print '%d/%d' % (idx,len(groups))
        group = list(group)
        for period, contract_ids in groupby_period(pending(obj, group)):
            if not period or not contract_ids:
                continue
            print 'Period: %s Contracts: %s' % (period, contract_ids)
            contract_obj.send_empowering_report(contract_ids, context={'period': period})
