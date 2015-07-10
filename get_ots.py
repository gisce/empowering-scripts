for ot in ('ot101', 'ot103', 'ot201'):
    for year in (201400, 201500):
        for month in range(1, 13):
            ts = year + month
            otobj = locals()[ot]
            otobj.pull_contract('00133', ts)