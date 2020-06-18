import click

from .server import run_server_by_urls


def run_server(host, port, publish, publish_name=''):
    """
    Gets a pointer to a function and inserts it dynamically to the handlers subdirectory.
    Then runs the system. The function's name can be given as an argument, while the default name
    is `handle_publish_mind`, since mind is the default protocol.
    """
    if publish_name == '':
        name = 'handle_publish_mind'
        scheme = 'publish'
    else:
        name = publish_name
        scheme = publish_name.split('_')[1]
    from .handlers import handler_rabbitmq_mind
    handler_rabbitmq_mind.__dict__[name] = publish
    return run_server_by_urls(f'http://{host}:{port}?framework=flask',
                              f'{scheme}://')


@click.command(name='run-server')
@click.option('-h', '--host', default='127.0.0.1', help='IP of the server')
@click.option('p', '--port', default=8000, help='PORT of the server')
@click.argument('url', default='rabbitmq://guest:guest@localhost:5672')
def run_server(host, port, path):
    """ URL: url to an already implemented publishing method:
    'scheme://username:password@host:port/path?queries'
    if scheme is rabbitmq then path is the exchange name and
    queries contains the routing keys for user and snapshot.
    example: 'rabbitmq://guest:guest@localhost:5672/inmymind&route_user=saver&route_snapshot=parser'
    NOTE: these parameters are the default, one can insert un empty string
    as url and get the same behaviour') """
    return run_server(host, port, path)
