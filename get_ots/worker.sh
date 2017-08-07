#!/bin/bash
. ~/conf/empowering_vars.sh
export PYTHONPATH=~/src/empowering-scripts/get_ots
export PATH=~/bin:$PATH

PEEK_SERVER=${PEEK_SERVER} PEEK_DB=${PEEK_DB} PEEK_USER=${PEEK_USER} PEEK_PASSWORD=${PEEK_PASSWORD} exec rqworker empowering_results_pull
