"""The job of Server's Getter is to get the messages from the client and to forward then
to the Server's Handler. He does not know the content not the format of the message nor
the protocol of the system.
The Handler is interfered from both the ``handler_url`` argument and the content_type of the
message (by definition of the protocols in this platform, every message has a content type the indicates
what is the protocol and what is the message's type.
"""


import logging
from urllib.parse import urlparse

from flask import Flask, request, Response

from inmymind._project_utils import dynamic_import
from inmymind.server._server_utils import find_handler

logger = logging.getLogger(__name__)


DEFAULT_HOST_FLASK = 'localhost'
DEFAULT_PORT_FLASK = 8000
DEFAULT_DEBUG_FLASK = False
DEFAULT_USE_RELOADER_FLASK = False
DEFAULT_SCHEME_HANDLER = 'rabbitmq'

def getter_foo_bar(getter_url, handler_url):
    """
    getter is a function. If ones prefers a class, it must has a ``get_message`` function with the same signature, and
    to the __init__ function must get the `getter_url`.
    Getter's name must be getter_*protocol*_*framework*. Here, the protocol is `foo` and the framework is `bar`.
    It has to call :func:`inmymind.server._server_utils import find_handler`
    The output format is a dict contains the keys: ``data`` and ``content_type``.
    The specific values are described in the relevant protocol.

    The Server's getter, must be in the `getters subdirectory` of ``server subpackge``
    (as a separate module ot in an existing module).
    """


def getter_http_flask(raw_getter_url, raw_handler_url):
    """Server's getter using HTTP protocol and Flask framework"""

    url = urlparse(raw_getter_url)
    host = url.hostname if url.hostname else DEFAULT_HOST_FLASK
    port = url.port if url.port else DEFAULT_PORT_FLASK
    options = {option.split('=')[0]: option.split('=')[1] for option in url.query.split('&')}
    debug = options.get('debug', DEFAULT_DEBUG_FLASK)
    use_reloader = options.get(DEFAULT_USE_RELOADER_FLASK)

    handlers = dynamic_import('handlers', 'handle_message', 'handler', raw_handler_url)
    url_handler = urlparse(raw_handler_url)
    handler_scheme = url_handler.scheme if url_handler.scheme else DEFAULT_SCHEME_HANDLER
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def get_message():
        try:
            handler = find_handler(handlers, handler_scheme, request.content_type)
            handler(request.data, request.content_type)
        except Exception as e:
            return Response(str(e), 400)
        return '', 200

    try:
        app.run(host, port, debug=debug, use_reloader=use_reloader)
    except (Exception, KeyboardInterrupt) as error:
        logger.warning(str(error))
        logger.info('closing handlers')
        for handler in handlers.values():
            handler(None, '')
        logger.info('closing app')
