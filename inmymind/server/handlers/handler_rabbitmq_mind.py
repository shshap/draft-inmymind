"""The job of Server's Getter is to get the messages from the client and to forward it
to the Server's Handler. He does not know the content nor the format of the message nor
the protocol of the system.
The Handler is interfered from both the ``handler_url`` argument and the content_type of the
message (by definition of the protocols in this platform, every message has a content type the indicates
what is the protocol and what is the message's type.
"""

import gzip
import logging
import os
import struct
from stat import S_IREAD
from urllib.parse import urlparse

import pika

logger = logging.getLogger(__name__)

DEFAULT_HOST_RABBITMQ = 'localhost'
DEFAULT_PORT_RABBITMQ = 27017
DEFAULT_USERNAME_RABBITMQ = 'guest'
DEFAULT_PASSWORD_RABBITMQ = 'guest'
DEFAULT_EXCHANGE_NAME_RABBITMQ = 'inmymind'
DEFAULT_USER_ROUTING_KEY = 'saver'
DEFAULT_SNAPSHOT_ROUTING_KEY = 'parser'
ACTIVE_PARSERS_QUEUES_LIST = ['parser_pose', 'parser_feelings',
                              'parser_color_image', 'parser_depth_image']
SNAPSHOT_PATH = '../snapshots/inmymind_%d_%d.mindbin.gz'  # user_id, datetime


def handler_foo_bar(data, content_type):
    """
    getter is a function. If ones prefers a class, it must has a ``handle_message`` function with the same signature, and
    to the __init__ function must get the `handler_url` argument.
    Handler's name must be handler_*scheme*_*protocol*. Here, the scheme is `foo` and the protocol is `bar`.
    The output format is following the protocol.

    The Server's handler, must be in the `handlers subdirectory` of ``server subpackge``
    (as a separate module ot in an existing module).
    """


class Handler_Rabbitmq_Mind:

    def __init__(self, raw_url=''):
        url = urlparse(raw_url)
        self.host = url.hostname if url.hostname else DEFAULT_HOST_RABBITMQ
        self.port = url.port if url.port else DEFAULT_PORT_RABBITMQ
        self.user = url.username if url.username else DEFAULT_USERNAME_RABBITMQ
        self.pswd = url.password if url.password else DEFAULT_PASSWORD_RABBITMQ
        self.x_name = url.path if url.path else DEFAULT_EXCHANGE_NAME_RABBITMQ
        self.dict_queries = {attr.split('=')[0]: attr.split('=')[1] for attr in url.query.split('&')}

        self._set_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.x_name, exchange_type='direct')
        self._declare_queues(['saver'] + ACTIVE_PARSERS_QUEUES_LIST)
        print('done setting channel and connection')

    def _set_connection(self):
        credentials = pika.PlainCredentials(self.user, self.pswd)
        parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)

    def _declare_queues(self, q_names):
        self.routing_key_user = self.dict_queries.get('route_user', DEFAULT_USER_ROUTING_KEY)
        self.routing_key_snapshot = self.dict_queries.get('route_snapshot', DEFAULT_SNAPSHOT_ROUTING_KEY)
        self.channel.queue_declare(queue='saver', durable=True)
        self.channel.queue_bind(exchange=self.x_name, queue='saver', routing_key=self.routing_key_snapshot)
        for q_name in ACTIVE_PARSERS_QUEUES_LIST:
            self.channel.queue_declare(queue=q_name, durable=True)
            self.channel.queue_bind(exchange=self.x_name, queue=q_name, routing_key=self.routing_key_snapshot)

    def close(self):
        self.connection.close()

    def handle_message(self, data, content_type):
        logger.debug(f'got message')
        if data is None:
            self.close()
            return
        data_type = content_type.split('/')[1]
        if data_type == 'user':
            logger.debug('got a user')
            self._handle_user(data)
        elif data_type == 'snapshot':
            logger.debug('got a snapshot')
            self._handle_snapshot(data)
        else:
            raise ValueError(f'Unknown message type: {data_type}')

    def _handle_user(self, message):

        self.channel.basic_publish(
            exchange=self.x_name,
            routing_key=self.routing_key_user,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2,
                                            content_type='mind/user')
        )
        logger.debug('sent user to saver')

    # minimum work for server
    def _handle_snapshot(self, message: bytes):
        path = self._write_snapshot_to_file(message)
        self.channel.basic_publish(
            exchange=self.x_name,
            routing_key=self.routing_key_snapshot,
            body=path,
            properties=pika.BasicProperties(delivery_mode=2,
                                            content_type='mind/snapshot')
        )
        logger.debug('sent snapshot to parsers')

    def _write_snapshot_to_file(self, raw_message):
        user_id, = struct.unpack('I', raw_message[:4])
        datetime, = struct.unpack('L', raw_message[4:12])
        logger.debug(f'{datetime=}')
        path = SNAPSHOT_PATH % (user_id, datetime)  # generate with generator
        with gzip.open(path, 'wb') as writer:
            writer.write(struct.pack('I', user_id))
            writer.write(raw_message[12:])  # raw_snapshot
        os.chmod(path, S_IREAD)
        return path
