import logging

from inmymind.server._server_utils import find_getter

logger = logging.getLogger(__name__)


def run_server_by_urls(getter_url, handler_url):
    """
        Determines the server's behaviour using urls.

        Args:

        getter_url - The url of the
        Must be consistent with the ``writer_url`` argument of the server,
        otherwise, it will cause unexpected behaviour.
        format: scheme://hostname:password@host:port/path?queries.
        example: ``http://localhost:8000?framework=flask&debug=True&use_reloader=True'``.

        handler_url: The url of the data destination.
        format: as above.
        example: ``rabbitmq://guest:guest@localhost:5672/inmymind&route_user=saver&route_snapshot=parser``

        Returns:
        0 - Successfully done reading the sample. 1 - Failure.
        """
    get_method = find_getter(getter_url)
    logger.debug('start serving')
    get_method(getter_url, handler_url)


if __name__ == '__main__':
    run_server_by_urls(
        'http://localhost:8000?framework=flask&debug=True&use_reloader=True',
        'rabbitmq://guest:guest@localhost:5672/inmymind&route_user=saver&route_snapshot=parser')
