from urllib.parse import urlparse

from inmymind._project_utils import dynamic_import

DEFUALT_INPUT_SCHEME = 'file'
DEFAULT_FILE_FORMAT = 'gz'
DEFUALT_INPUT_CONTENT_FORMAT = 'mind'
DEFUALT_UPLOAD_CONTENT_FORMAT = 'mind'
DEFUALT_UPLOAD_FORMAT = 'bin'


# For ones convenience, here is dynamic_import signature:
# dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
#                  first_word='', url=''

def find_driver(raw_url):
    # driver can only be a class because it has to expose an API
    drivers = dynamic_import('drivers', None, 'Driver', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFUALT_INPUT_SCHEME
    for (method_scheme,), method in drivers.items():
        if method_scheme == scheme:
            return method
    raise ValueError(f'no available driver for scheme {scheme}')


def find_reader(raw_url):
    readers = dynamic_import('readers', 'read', 'reader', raw_url)
    url = urlparse(raw_url)
    scheme = url.scheme if url.scheme else DEFUALT_INPUT_CONTENT_FORMAT
    for (method_scheme,), method in readers.items():
        if method_scheme == scheme:
            return method
    raise ValueError(f'no available reader for {scheme} protocol')


def find_writer(raw_url):
    writers = dynamic_import('writers', 'write', 'writer', raw_url)
    url = urlparse(raw_url)
    upload_scheme = url.scheme if url.scheme else DEFUALT_INPUT_CONTENT_FORMAT
    for (method_scheme,), method in writers.items():
        if method_scheme == upload_scheme:
            return method
    raise ValueError(f'no available writers to for scheme {upload_scheme}')
