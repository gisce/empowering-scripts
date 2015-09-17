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

def get_ots_contract(contract):
    for ot in ('ot101', 'ot103', 'ot201', 'ot401'):
        for year in (201300, 201400, 201500):
            for month in range(1, 13):
                ts = year + month
                pull_result.delay(contract, ot, ts)

def get_ots_all_contracts():
    contracts = e.contracts().multiget()
    for contract in contracts['_items']:
        get_ots_contract(contract['contractId'])