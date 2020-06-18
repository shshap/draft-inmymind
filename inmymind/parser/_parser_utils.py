import logging
from urllib.parse import urlparse

from inmymind._project_utils import dynamic_import

logger = logging.getLogger(__name__)

DEFAULT_SCHEME_GETTER = 'rabbitmq'
DEFAULT_TAG_PARSER = 'depth_image'  # just becuase it seems to be the most havy parser, so the more the merrier
DEFAULT_PROTOCOL_PARSER = 'mind'
DEFAULT_SCHEME_SENDER = 'rabbitmq'
DEFAULT_PARSER_TAG = 'depth_image'


# For ones convenience, here is dynamic_import signature:
# dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
#                  first_word='', url=''


def find_getter(raw_url):
    getters = dynamic_import('getters', 'get_message', 'getter', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_GETTER
    for (item_scheme,), method in getters.items():
        if item_scheme == scheme:
            return method
    raise ValueError(f'no available getter for {scheme} scheme')


def find_sender(raw_url):
    getters = dynamic_import('senders', 'send', 'sender', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_SENDER
    for (item_scheme,), method in getters.items():
        if item_scheme == scheme:
            return method
    raise ValueError(f'no available sender for {scheme} scheme')


def find_parser(parsers, content_type=None):
    protocol = content_type.split('/')[0]
    for (method_protocol), method in parsers.items():
        if method_protocol == protocol:
            return method
    raise ValueError(f'no available parser for {protocol} protocol')


def find_parse_method(raw_url):
    parse_methods = dynamic_import('parsers', 'parse', 'parse', raw_url)
    url = urlparse(raw_url)
    parser_tag = url.scheme.replace('_', '') if url.scheme else DEFAULT_TAG_PARSER
    for (tag,), method in parse_methods.items():
        if tag == parser_tag:
            return method
    raise ValueError(f'no available {url.scheme} parse method')
