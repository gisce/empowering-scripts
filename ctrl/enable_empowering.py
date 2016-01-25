import os
import ooop
import click

config = {
    'uri': os.getenv('PEEK_SERVER', None),
    'dbname': os.getenv('PEEK_DB', None),
    'user': os.getenv('PEEK_USER', None),
    'password': os.getenv('PEEK_PASSWORD', None)
}

def list_from_file(path):
    import csv

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [int(row[0]) for row in reader]

def get_partners(obj, contract_ids):
    partner_ids = []
    for contract in obj.GiscedataPolissa.read(contract_ids, ['titular', 'pagador']):
        partner_ids += contract['titular'][0]
        partner_ids += contract['pagador'][0]
    return partner_ids

def enable_emp_partner(obj, partner_ids):
    obj.ResPartner.assign_token(partner_ids)

def enable_emp_contract(obj, contract_ids):
    partner_ids = get_partners(obj, contract_ids)
    enable_emp_partner(list(set(partner_ids)))
    obj.GiscedataPolissa.write(contract_ids, {'empowering_profile_id':1})

@click.group()
@click.pass_context
def erp(ctx):
    from urlparse import urlparse

    config = ctx.obj['config']
    try:
        url = urlparse(config['uri'])
        ctx.obj['erp'] = ooop.OOOP(
             uri='{scheme}://{hostname}'.format(**{'scheme':url.scheme, 'hostname':url.hostname}),
             port=url.port,
             dbname=config['dbname'],
             user=config['user'],
             pwd=config['password']
             )
    except Exception, ex:
        click.echo('ERP connection failed')
        click.echo(ex)


@erp.command()
@click.pass_context
@click.argument('filename', type=click.Path(exists=True))
def enable_partner(ctx, filename):
    enable_emp_partner(ctx.obj['erp'], list_from_file(filename)

@erp.command()
@click.pass_context
@click.argument('filename', type=click.Path(exists=True))
def enable_contract(ctx, ids, filename):
    enable_emp_contract(ctx.obj['erp'], list_from_file(filename)

if __name__ == '__main__':
    erp(obj={'config': config})
