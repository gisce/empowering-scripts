import os
import erppeek
import ramman 
import click
import report
import utils

config = {
    'uri': os.getenv('PEEK_SERVER', None),
    'dbname': os.getenv('PEEK_DB', None),
    'user': os.getenv('PEEK_USER', None),
    'password': os.getenv('PEEK_PASSWORD', None),
    'heman': os.getenv('HEMAN_URL', None)
}

@click.group()
@click.pass_context
def erp(ctx):
    from urlparse import urlparse

    config = ctx.obj['config']
    try:
        url = urlparse(config['uri'])
        ctx.obj['erp'] = erppeek.Client( 
             '{scheme}://{hostname}:{port}'.format(
                                  **{'scheme':url.scheme,
                                     'hostname':url.hostname,
                                     'port':url.port}),
             config['dbname'],
             config['user'],
             config['password']
             )
        ctx.obj['heman'] = ramman.Ramman({'url': config['heman']})
    except Exception, ex:
        click.echo('ERP connection failed')
        click.echo(ex)


@erp.command()
@click.pass_context
@click.argument('filename', type=click.Path(exists=True))
def deliver(ctx, filename):
    report.deliver(ctx.obj, utils.list_from_file(filename))

@erp.command()
@click.pass_context
def deliver_all(ctx, filename):
    report.deliver(ctx.obj, None)

if __name__ == '__main__':
    erp(obj={'config': config})
