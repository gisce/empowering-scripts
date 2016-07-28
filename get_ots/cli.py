import logging
from get_ots import get_ots_contracts as  get_ots_contracts_, get_ots_all_contracts as get_ots_all_contracts_
import click

def list_from_file(path):
    import csv

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]

@click.group()
def emp():
    logging.basicConfig(level=logging.DEBUG)

@emp.command()
@click.option('--period', default=None)
def get_ots_all_contracts(period):
    get_ots_all_contracts_(period=period)

@emp.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--period', default=None)
def get_ots_contracts_from_file(filename, period=None):
    get_ots_contracts_(list_from_file(filename), period)

if __name__ == '__main__':
    emp(obj={})
    get_ots_all_contracts_()
