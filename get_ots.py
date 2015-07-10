def get_ots_contract(contract):
    for ot in ('ot101', 'ot103', 'ot201', 'ot401'):
        for year in (201400, 201500):
            for month in range(1, 13):
                ts = year + month
                otobj = locals()[ot]
                otobj.pull_contract(contract, ts)