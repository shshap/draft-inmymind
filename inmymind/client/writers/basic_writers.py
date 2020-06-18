"""
The job of Client's Writer is to write/send the data he got from the reader, to the destination.
The destination is interfered from the url, if possible.
Otherwise, the default is ``http://127.0.0.1:8000/``.
Gets the item and content type in the format:

"""

import gzip
import logging
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

DEFAULT_HOST_HTTP = '127.0.0.1'
DEFAULT_PORT_HTTP = 8000
DEFAULT_PATH_HTTP = '/'
DEFAULT_UPLOAD_FILE_PATH = './item_%d.gz'


def writer_example(raw_url, item=None):
    """
    writer is a function. If ones prefers a class, it has a ``write`` function with the same signature, and
    to the __init__ function must get the writer_url.
    Writer's name must be writer_*scheme*. Here, the scheme is 'example'.
    It accepts item of which is a dict with the keys ``data`` and ``content_type``.

    The Client's writer, must be in the `writers subdirectory` of ``client subpackge``
    (as a separate module ot in an existing module).
    """


def writer_http(raw_url, item=None):
    """Client's writer that using HTTP protocol for sending the data"""

    logger.debug('in write_http_bin')
    url = urlparse(raw_url)
    host = url.hostname if url.hostname else DEFAULT_HOST_HTTP
    port = url.port if url.port else DEFAULT_PORT_HTTP
    path = url.path if url.path else DEFAULT_PATH_HTTP
    while True:
        try:
            r = requests.post(f'http://{host}:{port}{path}',
                              data=item['data'],
                              headers={'Content_type': item['content_type']})
            break
        except requests.exceptions.ConnectionError:
            logger.info('connection error, try again in 5 sec')
            sleep(5)

    logger.debug('send request')
    if r.status_code != 200:
        logger.info(f'server rejected: {r.text}')
        return 2
    return 0


class writer_file:
    """Client's writer that writes the data to a local file"""

    def __init__(self, raw_url):
        url = urlparse(raw_url)
        if url.path:
            self.path = url.path
        else:
            raise ValueError(f'bad write path {url.path}')
        file_format = Path(self.path).suffix
        if file_format == 'gz':
            self.open = gzip.open
        else:
            self.open = open
        self.counter = 0

    def write(self, data):
        self.counter += 1
        path = DEFAULT_UPLOAD_FILE_PATH % self.counter
        with self.open(path, 'ab') as writer:
            if type(data) != bytes:
                data = data.encode('utf-8')
            writer.write(data)
