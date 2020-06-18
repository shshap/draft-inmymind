import click

from ._parser_utils import find_parser
from .parser import run_parser_by_urls


def run_parser(parser_tag='', data=b''):
    raw_parser_url = f'{parser_tag}://'
    content_type = 'mind/snapshot'
    parser = find_parser(raw_parser_url, content_type)
    return parser(data, sender=None)


@click.command(name='parse')
@click.argument('parser_tag', default='depth_image')
@click.argument('path')
def run_parser_path(parser_tag='', path=''):
    """
    PARSER_TAG: pose/feelings/depth_image[default]/color_image
    PATH:  path to raw snapshot.
    NOTE: the raw snapshot's format is mindbin, i.e.
    b'<user_id><serializes_snapshot_in_mind_format>
    as mind refers to cortex.proto
    """
    raw_parser_url = f'{parser_tag}://'
    content_type = 'mind/snapshot'
    parser = find_parser(raw_parser_url, content_type)
    return parser(path, sender=None)


@click.command(name='run-parser')
@click.argument('parser_tag', default='depth_image')
@click.argument('getter_url', default='rabbitmq://guest:guest@localhost:5672')
@click.argument('sender_url', default='rabbitmq://guest:guest@localhost:5672')
def run_parser_cli_mq(parser_tag='', url=''):
    """
    PARSER_TAG: pose/feelings/depth_image[default]/color_image

    GETTER_URL: url to an already implemented getter method:'
    scheme://username:password@host:port/path?queries'
    if scheme is rabbitmq then path is the exchange name
    and the queries contains the queue name and the routing key it accepts.
    example: rabbitmq://guest:guest@localhost:5672/inmymind&q_name=parser_depth_image&routing_key=parser
    NOTE: these parameters are the default, one can insert un empty string
    as url and get the same behaviour

    SENDER_URL: url to an already implemented sender method:
    format is the same as the getter_url.
    if scheme is rabbitmq then the path is the exchange name
    and the queries contains the queue name and the routing key it accepts.
    example: rabbitmq://guest:guest@localhost:5672/inmymind&q_name=parser_pose&routing_key=saver
    NOTE: these parameters are the default, one can insert un emprty string
    as url and get the same behaviour"""

    run_parser_by_urls(url, f'{parser_tag}://', url)
