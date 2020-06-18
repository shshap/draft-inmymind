import logging
from urllib.parse import urlparse

from inmymind._project_utils import dynamic_import

logger = logging.getLogger(__name__)

DEFAULT_SCHEME_GETTER = 'rabbitmq'
DEFAULT_SCHEME_HANDLER = 'http'

# For ones convenience. here is dynamic_import signature:
# dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
#                  first_word='', url=''



# testing: moking the find_drivers: lecture 7 part 3 minute 36
def find_getter(raw_url):
    getters = dynamic_import('getters', 'run', 'getter', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_GETTER
    for (item_scheme,), method in getters.items():
        if item_scheme == scheme:
            return method
    raise ValueError(f'no available getter for {scheme} scheme')


def find_handler(raw_url, content_type='/'):
    handlers = dynamic_import('handlers', 'handle_message', 'handler', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_HANDLER
    message_format = content_type.split('/')[0]
    for (method_scheme, format), method in handlers.items():
        if method_scheme == scheme and format == message_format:
            return method
    raise ValueError(
        f'no available handler for  scheme {scheme} and format {message_format}')
