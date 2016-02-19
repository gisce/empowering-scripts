import logging
from get_ots import get_ots_contracts as  get_ots_contracts_orig, get_ots_all_contracts as get_ots_all_contracts_orig
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
def get_ots_all_contracts():
    get_ots_all_contracts_orig()

@emp.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--ts', default=None)
def get_ots_contracts(filename, ts=None):
    get_ots_contracts_orig(list_from_file(filename))

if __name__ == '__main__':
    emp(obj={})
    get_ots_all_contracts_orig()
