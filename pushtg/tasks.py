# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import logging
import urllib2

import libsaas

from utils import (
    setup_peek, setup_mongodb, setup_empowering_api, setup_redis,
    sorted_by_key, Popper, setup_queue
)
import pymongo
from rq.decorators import job
from raven import Client
from empowering.utils import make_local_timestamp


sentry = Client()
logger = logging.getLogger('pushtg')


def enqueue_measures(contracts_id=[], bucket=500):
    # First get all the contracts that are in sync
    O = setup_peek()
    em = setup_empowering_api()

    search_params = [('etag', '!=', False),
                     ('state', '=', 'activa'),
                     ('cups.empowering', '=', True)]
    if isinstance(contracts_id, list) and contracts_id:
        search_params.append(('id', 'in', contracts_id))
    pids = O.GiscedataPolissa.search(search_params)

    fields_to_read = ['name', 'comptadors', 'cups']
    contracts = O.GiscedataPolissa.read(pids[:5], fields_to_read)

    popper = Popper([])
    popper.push(contracts)
    pops = popper.pop(bucket)

    start = datetime.now() - relativedelta(days=15)
    while pops:
        #j = push_measures.delay(pops)
        j = push_contract(pops, start)
        #logger.info("Job id:%s | %s/%s" % (
        #     j.id, len(pops), len(popper.items))
        #)
        pops = popper.pop(bucket)


#@job(setup_queue(name='measures'), connection=setup_redis(), timeout=3600)
#@sentry.capture_exceptions
def push_contract(contracts, start):
    em = setup_empowering_api()
    mongo = setup_mongodb()
    collection = mongo['tg_cchfact']

    for contract in contracts:
        name = contract['name']
        meters = contract['comptadors']
        cups = contract['cups'][1] 

        cups='ES0031448330978025MT0F'
        mdbmeasures = collection.find({'name': cups},
                                      {'name': 1, 'id': 1, '_id': 0,
                                          'ai': 1, 'r1': 1, 'datetime':1},
                                      sort=[('datetime', pymongo.ASCENDING)])
        measures = [x for x in mdbmeasures]
        print measures

#    start = datetime.now()
#    if tg_enabled:
#    else:
#        fields_to_read = ['comptador', 'name', 'tipus', 'periode', 'lectura']
#
#        measures = O.GiscedataLecturesLectura.read(measures_ids, fields_to_read)
#        # NOTE: Tricky end_date rename
#        for idx, item in enumerate(measures):
#            measures[idx]['date_end']=measures[idx]['name']
#
#    logger.info("Enviant de %s (id:%s) a %s (id:%s)" % (
#        measures[-1]['date_end'], measures[-1]['id'],
#        measures[0]['date_end'], measures[0]['id']
#    ))
#    measures_to_push = amon.measure_to_amon(measures)
#    stop = datetime.now()
#    logger.info('Mesures transformades en %s' % (stop - start))
#    start = datetime.now()
#
#    measures_pushed = em.residential_timeofuse_amon_measures().create(measures_to_push)
#    # TODO: Pending to check whether all measure were properly commited
#
#    if tg_enabled:
#        for measure in measures:
#            from .amon import get_device_serial
#
#            serial = get_device_serial(last_measure['name'])
#            cids = O.GiscedataLecturesComptador.search([('name', '=', serial)], context={'active_test': False})
#            O.GiscedataLecturesComptador.update_empowering_last_measure(cids, '%s' % measure['date_end'])
#        mongo.connection.disconnect()
#    else:
#        for measure in measures:
#          O.GiscedataLecturesComptador.update_empowering_last_measure(
#                [measure['comptador'][0]], '%s' % measure['date_end'] 
#          )
#    stop = datetime.now()
#    logger.info('Mesures enviades en %s' % (stop - start))
#    logger.info("%s measures creades" % len(measures_pushed))
#

# vim: ts=4 sw=4 et
