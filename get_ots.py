import logging
import amoniak

logging.basicConfig(level=logging.DEBUG)

e = amoniak.utils.setup_empowering_api()
m = amoniak.utils.setup_mongodb()

def get_ots_contract(contract):
    ot101 = amoniak.caching.OT101Caching(e, m)
    ot103 = amoniak.caching.OT103Caching(e, m)
    ot201 = amoniak.caching.OT201Caching(e, m)
    ot401 = amoniak.caching.OT401Caching(e, m)
    
    for ot in (ot101, ot103, ot201, ot401):
        for year in (201400, 201500):
            for month in range(1, 13):
                ts = year + month
                otobj = locals()[ot]
                otobj.pull_contract(contract, ts)