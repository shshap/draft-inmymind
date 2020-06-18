import logging
from urllib.parse import urlparse

from inmymind._project_utils import dynamic_import

logger = logging.getLogger(__name__)

DEFAULT_SCHEME_DB = 'mongo'
DEFAULT_SCHEME_API = 'http'
DEFAULT_FRAMEWORK_BY_CHEME = {'http': 'flaskrestful'}


# For ones convenience, here is dynamic_import signature:
# dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
#                  first_word='', url=''


# testing: moking the find_drivers: lecture 7 part 3 minute 36
def find_db_service(raw_url):
    db_services = dynamic_import('db_services', None, 'DbService', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_DB
    for (cls_scheme,), cls in db_services.items():
        if scheme == cls_scheme:
            return cls(url)
    raise ValueError(f'no available db service for scheme {scheme}')


def find_api_service(raw_url):
    db_services = dynamic_import('api_services', 'run', 'Api', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFAULT_SCHEME_API
    queries = {attr.split('=')[0]: attr.split('=')[1] for attr in raw_url.query.split('&')}
    framework = queries.get('framework', DEFAULT_FRAMEWORK_BY_CHEME)
    for (method_scheme, method_framework), method in db_services.items():
        if method_scheme == scheme and method_framework == framework:
            return method
    raise ValueError(f'no available api service for scheme {scheme} ans framework {framework}')
