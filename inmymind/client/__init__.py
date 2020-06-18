import click


from .client import upload_sample_by_urls


def upload_sample(host, port, path):
    return upload_sample_by_urls(f'file://{path}',
                                 f'http://{host}:{port}/')


@click.command(name='upload-sample')
@click.option('--host', '-h', default='127.0.0.1', help='IP of the server')
@click.option('--port', 'p', default=8000, type=int, help='PORT of the server')
@click.argument('path', type=click.Path())
def upload_sample(host, port, path):
    """ PATH: path to sample [<name>.<content_format>.<file_format>]"""
    return upload_sample(host, port, path)
