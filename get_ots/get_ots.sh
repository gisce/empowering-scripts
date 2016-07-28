. ~/conf/empowering_vars.sh
MONTH_0=`date +'%Y%m'`
MONTH_1=`date --date="-1 month" +'%Y%m'`
MONTH_2=`date --date='-2 month' +'%Y%m'`
PYTHONPATH=~/src/erp/server/sitecustomize/ python ~/src/empowering-scripts/get_ots/cli.py get_ots_all_contracts --period $MONTH_2 
PYTHONPATH=~/src/erp/server/sitecustomize/ python ~/src/empowering-scripts/get_ots/cli.py get_ots_all_contracts --period $MONTH_1
PYTHONPATH=~/src/erp/server/sitecustomize/ python ~/src/empowering-scripts/get_ots/cli.py get_ots_all_contracts --period $MONTH_0 
