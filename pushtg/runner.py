#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

import click

import utils
import tasks

@click.group()
@click.option('--log-level', default='info')
@click.option('--async/--no-async', default=True)
def pushtg(log_level, async):
    MODE = {True: 'ASYNC', False: 'SYNC'}
    log_level = log_level.upper()
    log_level = getattr(logging, log_level, 'INFO')
    logging.basicConfig(level=log_level)
    utils.setup_logging()
    logger = logging.getLogger('pushtg')
    os.environ['RQ_ASYNC'] = str(async)

@pushtg.command()
@click.option('--contracts', default=[])
def enqueue_measures(contracts):
    logger = logging.getLogger('pushtg')
    logger.info('Enqueuing measures')
    tasks.enqueue_measures(contracts,bucket=4)

if __name__ == '__main__':
    pushtg(obj={})
