"""The job of the Client's Driver is to get the sample.
The protocol and the file format are interfered from the url.
Otherwise, throws ValueError exception.
Every driver exposes a API as in the next example:"""

import gzip
import logging
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


class Driver_example:
    """
    Driver must be a class since it has the expose an API.
    Driver's name must be Driver_*scheme*. Here, the scheme is 'example'.
    In initialization, gets the driver_url.
    Opening the sample, if needed, happens during the Driver object initialization.

    The Client's Driver, must be in the `drivers subdirectory` of ``client subpackge``
    (as a separate module ot in an existing module).
    """

    def read(self, size):
        """returns the next `size` bytes from the sample."""

    def close(self):
        """Closure procedure, if needed. This method will be called right before exiting the program."""


class Driver_File:
    """Client's Driver that handles local files"""
    def __init__(self, raw_url):
        url = urlparse(raw_url)
        if url.path:
            self.path = url.path
        else:
            raise ValueError('no path is given')
        file_format = Path(self.path).suffix
        if file_format == 'gz':
            self.open_func = gzip.open
        else:
            self.open_func = open
        try:
            self.sample = self.open_func(self.path, 'rb')
        except Exception as error:
            raise ValueError(f'bad driver path: {str(error)}')

    def read(self, size):
        logger.debug('in read')
        return self.sample.read(size)

    def close(self):
        logger.debug('in close')
        if self.sample is None:
            return
        self.sample.close()
