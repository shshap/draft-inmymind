import inspect
import os
from functools import partial
import logging
from pathlib import Path
from urllib.parse import urlparse

from inmymind.client._client_utils import find_driver, find_reader, find_writer

logger = logging.getLogger(__name__)

READER_URL = '%s://'


class Manager:
    """The main class of the client. Abstract Handler of the connections between the Driver, the Reader and the
    Writer. Does not aware to to protocol. """

    def __init__(self, driver_url, reader_url, writer_url):
        try:
            self.driver = find_driver(driver_url)
            self.reader = find_reader(reader_url)
            if inspect.isgeneratorfunction(self.reader):
                # going to give the reader the arguments, without cause the first read.
                # generator function can be given an argument that won't cause the first yield
                self.reader = self.reader(reader_url, self.driver)
            else:
                # functools.partial is the solution for regular function
                self.reader = partial(self.reader, reader_url, self.driver)
            self.writer = find_writer(writer_url)
        except Exception as error:
            self.stop()
            raise ValueError(f'bad url: {str(error)}')
        self.reader_type = self.reader.__name__ if hasattr(self.reader, '__name__') else type(self.reader).__name__
        self.sample = None  # fd
        self.items_counter = 0

    def run(self):
        logger.debug('in run')
        try:
            while True:
                ret = self._read_next_item()
                if ret == 0:
                    continue
                if ret == 1:
                    logger.info('client is done with success')
                    self.stop()
                    return 0
                if ret == 2:
                    logger.warning(f'error occurred while handling item number {self.items_counter}')
        except (Exception, KeyboardInterrupt) as error:
            logger.warning(str(error))
            logger.info('closing client')
            self.stop()
            return 1

    def _read_next_item(self):
        logger.debug('in read_next_item')
        item = next(self.reader) if self.reader_type == 'generator' else self.reader()
        if item is None:
            return 1
        self.items_counter += 1
        return self.writer(item)

    def stop(self):
        if hasattr(self, 'driver'):
            self.driver.close()


def upload_sample_by_urls(driver_url, writer_url):
    """
    Determines the client's behaviour using urls.

    Args:

    driver_url - The url of the sample.
    format: scheme://hostname:password@host:port/path?queries.
    The path extentions are <protocol>.<file_format>.
    example: ``file:///sample.mind.gz``. Here the protocol is :mod:`inmymind.protocols.mind`.

    writer_url: The url of the data destination. Must be consistent with the ``getter_url`` argument of the server,
    otherwise, it will cause unexpected behaviour.
    format: as above.
    example: ``http://127.0.0.1:8000/``

    Returns:
    0 - Successfully done reading the sample. 1 - Failure.
    """
    logger.debug('in handle_sample')
    try:
        protocol = Path(urlparse(driver_url).path).suffixes[-2]
    except Exception as error:
        protocol = 'mind://'
    reader_url = READER_URL % protocol
    manager = Manager(driver_url, reader_url, writer_url)
    try:
        return manager.run()
    except (Exception, KeyboardInterrupt) as error:
        logger.warning(str(error))
        logger.info('closing client')
        manager.stop()
        return 1


if __name__ == '__main__':
    upload_sample_by_urls(f'file:///{os.getcwd()}/mind/sample.mind.gz',
                          'http://127.0.0.1:8000/')
