import logging
from urllib.parse import urlparse

import pika

logger = logging.getLogger(__name__)

DEFAULT_HOST_RABBITMQ = 'localhost'
DEFAULT_PORT_RABBITMQ = 27017
DEFAULT_USERNAME_RABBITMQ = 'guest'
DEFAULT_PASSWORD_RABBITMQ = 'guest'
DEFAULT_EXCHANGE_NAME_RABBITMQ = 'inmymind'
DEFAULT_ROUTING_KEY_RABBITMQ_SENDER = 'saver'
DEFAULT_TAG_PARSER = 'depth_image'
DEFAULT_QUEUE_NAME = 'parser_depthimage'


class Sender_Rabbitmq:

    def __init__(self, raw_url=''):
        self.url = urlparse(raw_url)
        self.x_name = self.url.path if self.url.path else DEFAULT_EXCHANGE_NAME_RABBITMQ
        self.dict_queries = {attr.split('=')[0]: attr.split('=')[1] for attr in self.url.query.split('&')}
        self.tag_parser = self.dict_queries.get('tag', DEFAULT_TAG_PARSER)
        self._set_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.x_name, exchange_type='direct')
        self._declare_queue()
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
        q_name = self.dict_queries.get('q_name', DEFAULT_QUEUE_NAME)
        self.routing_key = self.dict_queries.get('routing_key', DEFAULT_ROUTING_KEY_RABBITMQ_SENDER)
        self.channel.queue_declare(queue=q_name, durable=True)
        self.channel.queue_bind(exchange=self.x_name, queue=q_name, routing_key=self.routing_key)

    def close(self):
        self.connection.close()

    def send(self, message: bytes, protocol):
        try:
            self.channel.basic_publish(
                exchange=self.x_name,
                routing_key=self.routing_key,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2,
                                                content_type=protocol + '/snapshot')
            )
        except Exception as error:
            logger.warning(str(error))
            return 1
        logger.debug('sent snpashot to saver')
        return 0
