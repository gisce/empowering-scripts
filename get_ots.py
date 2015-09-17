import logging
import amoniak
from amoniak import caching


logging.basicConfig(level=logging.DEBUG)

e = amoniak.utils.setup_empowering_api()
m = amoniak.utils.setup_mongodb()

def get_ots_contract(contract):
    ot101 = caching.OT101Caching(e, m)
    ot103 = caching.OT103Caching(e, m)
    ot201 = caching.OT201Caching(e, m)
    ot401 = caching.OT401Caching(e, m)
    
    for ot in (ot101, ot103, ot201, ot401):
        for year in (201400, 201500):
            for month in range(1, 13):
                ts = year + month
                ot.pull_contract(contract, ts)

def get_ots_all_contracts():
    contracts = e.contracts().multiget()
    for contract in contracts['_items']:
        get_ots_contract(contract['contractId'])