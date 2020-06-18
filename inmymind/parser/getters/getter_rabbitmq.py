import json
import logging
from functools import partial
from urllib.parse import urlparse

import pika

from inmymind._project_utils import dynamic_import
from inmymind.parser._parser_utils import find_parser

logger = logging.getLogger(__name__)

DEFAULT_HOST_RABBITMQ = 'localhost'
DEFAULT_PORT_RABBITMQ = 5672
DEFAULT_USERNAME_RABBITMQ = 'guest'
DEFAULT_PASSWORD_RABBITMQ = 'guest'
DEFAULT_EXCHANGE_NAME_RABBITMQ = 'inmymind'
DEFAULT_ROUTING_KEY_GETTER = 'parser'
DEFAULT_QUEUE_NAME_PARSER = 'parser_depthimage'


class Getter_Rabbitmq:

    def __init__(self, raw_getter_url=''):
        self.url = urlparse(raw_getter_url)
        self.x_name = self.url.path if self.url.path else DEFAULT_EXCHANGE_NAME_RABBITMQ
        self.dict_queries = {attr.split('=')[0]: attr.split('=')[1] for attr in self.url.query.split('&')}
        self._connect()

    def _connect(self):
        self._set_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.x_name, exchange_type='direct')
        self._declare_queue()
        self.is_consuming = False
        print('done setting channel and connection')

    def _set_connection(self):
        host = self.url.hostname if self.url.hostname else DEFAULT_HOST_RABBITMQ
        port = self.url.port if self.url.port else DEFAULT_PORT_RABBITMQ
        user = self.url.username if self.url.username else DEFAULT_USERNAME_RABBITMQ
        pswd = self.url.password if self.url.password else DEFAULT_PASSWORD_RABBITMQ

        credentials = pika.PlainCredentials(user, pswd)
        parameters = pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)

    def _declare_queue(self):
        self.q_name = self.dict_queries.get('q_name', DEFAULT_QUEUE_NAME_PARSER)
        routing_key = self.dict_queries.get('routing_key', DEFAULT_ROUTING_KEY_GETTER)
        self.channel.queue_declare(queue=self.q_name, durable=True)
        self.channel.queue_bind(exchange=self.x_name, queue=self.q_name, routing_key=routing_key)

    def run(self, raw_getter_url='', raw_parser_url='', sender=None):
        self.parsers = dynamic_import('parsers', 'parse', 'parser', raw_parser_url)
        self.channel.basic_consume(qugeue=self.q_name,
                                   on_message_callback=partial(self.callback, raw_parser_url, sender))
        self.channel.basic_qos(prefetch_count=1)
        try:
            logger.debug('start consuming')
            self.is_consuming = True
            self.channel.start_consuming()
        except KeyboardInterrupt:
            return 0
        except Exception as error:
            logger.fatal(str(error))
            return 1

    def stop(self):
        if self.is_consuming:
            self.channel.stop_consuming()
        self.connection.close()

    def callback(self, raw_parser_url, sender, ch, method, properties, body):
        logger.debug(f'dedicated a body! {json.loads(body)}')
        logger.debug('got type %r and content %r' % (type(body), body))
        if sender is None:
            ch.basic_reject(delivery_tag=method.delivery_tag)

        parser = find_parser(self.parsers, properties.content_type)
        ret = parser(body, properties.content_type, raw_parser_url, sender)
        if ret == 0:
            logger.debug('ack after success')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        elif ret == 1:
            logger.debug('reject after failure that can be fixed')
            ch.basic_reject(delivery_tag=method.delivery_tag)
            return
        else:
            logger.debug('ack after failure that cannot be fixed')
            ch.basic_ack(delivery_tag=method.delivery_tag)
