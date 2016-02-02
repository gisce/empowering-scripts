import logging
from get_ots import get_ots_contracts as  get_ots_contracts_orig,
                    get_ots_all_contracts as get_ots_all_contracts_orig
import click

logging.basicConfig(level=logging.DEBUG)

def list_from_file(path):
    import csv

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]

@click.group
def emp(log_level):
    logging.basicConfig(level=log_level)

@emp.command()
def get_ots_all_contracts():
    get_ots_all_contracts_orig()

@emp.command()
@click.argument('filename', type=click.Patch(exists=True))
def get_ots_contracts(filename):
    get_ots_contracts_orig(list_from_file(filename))

if __name__ == '__main__':
    get_ots_all_contracts_orig()
