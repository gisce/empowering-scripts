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

def disable_emp_contracts(obj, contracts):
    contracts_id = obj.GiscedataPolissa.search([('name', 'in', contracts)])
    obj.GiscedataPolissa.write(contracts_id, {'empowering_profile_id': False})

    cups_id = obj.GiscedataCupsPs.search([('polissa_polissa', 'in', contracts_id)])
    obj.GiscedataCupsPs.write(cups_id, {'empowering': False})

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
def disable_contracts(ctx, filename):
    disable_emp_contracts(ctx.obj['erp'], list_from_file(filename, str))

if __name__ == '__main__':
    erp(obj={'config': config})
