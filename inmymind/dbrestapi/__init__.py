import click

from .app import run_api_server_by_urls


def run_api_server(host, port, database_url):
    run_api_server_by_urls(
        f'http://{host}:{port}?framework=flaskrestful',
        database_url
    )


@click.command(name='run-server')
@click.option('-h', '--host', default='127.0.0.1', help='IP of the API server')
@click.option('--port', '-p', default=5000, help='PORT of the API server')
@click.argument('-d', '--database', default='mongo://localhost:27017/inmymind?alias=core')
def run_api_server_cli(host, port, database):
    """
    DATABASE: the database url. Has to expose a db service as explained
    in the docs. for example: mongo://localhost:27017/inmymind?alias=core
    when the path section is the db name
    Note: this example is the default
    """
    # the argument help is in the scope because of issues of click
    run_api_server(host, port, database)
