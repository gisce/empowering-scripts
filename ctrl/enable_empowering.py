import os
import ooop
import click

config = {
    'uri': os.getenv('PEEK_SERVER', None),
    'dbname': os.getenv('PEEK_DB', None),
    'user': os.getenv('PEEK_USER', None),
    'password': os.getenv('PEEK_PASSWORD', None)
}

def list_from_file(path, cast):
    import csv

    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [cast(row[0]) for row in reader]

def get_partners(obj, contracts_id):
    partners_id = []
    for contract in obj.GiscedataPolissa.read(contracts_id, ['titular', 'pagador']):
        partners_id.append(contract['pagador'][0])
    return partners_id

def enable_emp_partner(obj, partners_id):
    obj.ResPartner.assign_token(partners_id)

def enable_emp_contract(obj, contracts):
    contracts_id = obj.GiscedataPolissa.search([('name', 'in', contracts)])
    partners_id = get_partners(obj, contracts_id)
    enable_emp_partner(obj, list(set(partners_id)))
    obj.GiscedataPolissa.write(contracts_id, {'empowering_profile_id':1})

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
    enable_emp_partner(ctx.obj['erp'], list_from_file(filename, int))

@erp.command()
@click.pass_context
@click.argument('filename', type=click.Path(exists=True))
def enable_contract(ctx, filename):
    enable_emp_contract(ctx.obj['erp'], list_from_file(filename, str))

if __name__ == '__main__':
    erp(obj={'config': config})
