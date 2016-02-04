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
        return [row[0] for row in reader]

def send(obj, contract_ids):
    search_params = [('cups.empowering', '=', True),
                     ('cups.empowering_quarantine', '=', 1)]
    if contract_ids is not  None:
        search_params.append(('name', 'in', contract_ids))
    contract_ids = obj.GiscedataPolissa.search(search_params)
    obj.GiscedataPolissa.send_empowering_report(contract_ids)

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
def send_report(ctx, filename):
    send(ctx.obj['erp'], list_from_file(filename))

@erp.command()
@click.pass_context
def send_all_report(ctx, filename):
    send(ctx.obj['erp'], None)

if __name__ == '__main__':
    erp(obj={'config': config})
