import json
import logging

import pika

from urllib.parse import urlparse

from inmymind.saver._saver_utils import find_handler

logger = logging.getLogger(__name__)

DEFAULT_HOST_RABBITMQ = 'localhost'
DEFAULT_PORT_RABBITMQ = 27017
DEFAULT_USERNAME_RABBITMQ = 'guest'
DEFAULT_PASSWORD_RABBITMQ = 'guest'
DEFAULT_EXCHANGE_NAME_RABBITMQ = 'inmymind'
ACTIVE_PARSERS_QUEUES_LIST = ['parser_pose', 'parser_feelings',
                              'parser_color_image', 'parser_depth_image']


class Getter_Rabbitmq_mindjson:

    def __init__(self, raw_getter_url='', raw_handler_url=''):
        url = urlparse(raw_getter_url)
        self.host = url.hostname if url.hostname else DEFAULT_HOST_RABBITMQ
        self.port = url.port if url.port else DEFAULT_PORT_RABBITMQ
        self.user = url.username if url.username else DEFAULT_USERNAME_RABBITMQ
        self.pswd = url.password if url.password else DEFAULT_PASSWORD_RABBITMQ
        self.x_name = url.path if url.path else DEFAULT_EXCHANGE_NAME_RABBITMQ

        self._set_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.x_name, exchange_type='direct')
        self._declare_queues(['saver'] + ACTIVE_PARSERS_QUEUES_LIST)
        self.channel.basic_consume(queue='saver', on_message_callback=self.callback)
        self.channel.basic_qos(prefetch_count=1)
        self.is_consuming = False

        print('done setting channel and connection')

    def _set_connection(self):
        credentials = pika.PlainCredentials(self.user, self.pswd)
        parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)

    def _declare_queues(self, q_names):
        for q_name in q_names:
            self.channel.queue_declare(queue=q_name, durable=True)
            self.channel.queue_bind(exchange=self.x_name, queue=q_name, routing_key=q_name)

    def run(self):
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

    def callback(self, handler_url, ch, method, properties, body):
        logger.debug(f'dedicated a body! {json.loads(body)}')
        logger.debug('got type %r and content %r' % (type(body), body))
        handler = find_handler(handler_url, properties.content_type)
        body = body.decode('utf-8')
        ret = handler(body, properties.content_type)
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
