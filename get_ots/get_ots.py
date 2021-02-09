import logging
import amoniak
from amoniak import caching
from rq.decorators import job


logging.basicConfig(level=logging.DEBUG)

e = amoniak.utils.setup_empowering_api()
m = amoniak.utils.setup_mongodb()
queue = amoniak.utils.setup_queue(name='empowering_results_pull')
redis_conn = amoniak.utils.setup_redis()

@job(queue, connection=redis_conn, timeout=3600)
def pull_result(contract, ot, period):
    ot = get_ot_caching(ot)
    ot.pull_contract(contract, period)

def get_ot_caching(ot):
    attr = '{}Caching'.format(ot.upper())
    if not hasattr(caching, attr):
        raise Exception('{} not found!'.format(attr))
    return getattr(caching, attr)(e, m)

@job(queue, connection=redis_conn, timeout=3600)
def get_ots(ot, contract=[], period=None):
    ot_obj = get_ot_caching(ot)
    ot_obj.pull_contract(contract, period)

def get_all_ots(contracts=[], period=None):
    for ot in ('ot101', 'ot103', 'ot201', 'ot401'):
        get_ots.delay(ot, contracts, period)

def get_ots_all_contracts(period=None):
    get_all_ots(period=period)

def get_ots_contracts(contract_ids, period=None):
    for contract in contract_ids:
        get_all_ots(contract, period)
