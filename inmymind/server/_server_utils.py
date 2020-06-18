import logging
from urllib.parse import urlparse

from inmymind._project_utils import dynamic_import

logger = logging.getLogger(__name__)

DEFAULT_SCHEME_GETTER = 'http'
DEFAULT_FORMAT = 'mind'
DEFAULT_FRAMEWORK_BY_CHEME = {'http': 'flask'}


# For ones convenience. here is dynamic_import signature:
# dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
#                  first_word='', url=''


def find_getter(raw_url):
    getters = dynamic_import('getters', 'get_message', 'getter')
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_GETTER
    queries = {attr.split('=')[0]: attr.split('=')[1] for attr in raw_url.query.split('&')}
    framework = queries.get('framework', DEFAULT_FRAMEWORK_BY_CHEME)
    for (item_scheme, item_framework), method in getters.items():
        if item_scheme == scheme and item_framework == framework:
            return method
    raise ValueError(f'no available getter for {scheme} scheme')


def find_handler(handlers, handler_scheme, content_type=''):
    handler_format = content_type.split('/')[0] if content_type else DEFAULT_FORMAT
    for (method_scheme, method_format), method in handlers.items():
        if method_scheme == handler_scheme and method_format == handler_format:
            return method
    raise ValueError(
        f'no available handler for scheme {handler_scheme} and format {handler_format}')
