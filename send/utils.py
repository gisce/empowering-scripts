import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import itertools
import operator


def todatetime(datetime_str, totime):
    str_pattern = '%Y-%m-%d'
    if totime:
        str_pattern += ' %H:%M:%S'
    return  datetime.strptime(datetime_str, str_pattern)

def toperiod(datetime_obj):
    return datetime_obj.strftime('%Y%m')
   
def list_from_file(path):
    import csv

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]

def groupby_period(l):
    get_attr = operator.itemgetter(1)
    it = itertools.groupby(sorted(l, key=get_attr), get_attr)
    for key, subiter in it:
        yield key, [item[0] for item in subiter]
