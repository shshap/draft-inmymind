import logging

from inmymind.parser._parser_utils import find_getter, find_sender

logger = logging.getLogger(__name__)


def run_parser_by_urls(getter_url, parser_url, sender_url):
    logger.debug('in handle_sample')
    getter = find_getter(getter_url)
    sender = find_sender(sender_url)
    try:
        return getter(getter_url, parser_url, sender)
    except (Exception, KeyboardInterrupt) as error:
        logger.warning(str(error))
        logger.info('closing client')
        getter.stop()
        return 1


# getter and sender remains the same because they depend only on the url,
# and the parser is determined also by the type of the message.
# the getter and the sender are only mechanism, they are don't aware to the
# content type of the message, the logics of get/send and parse are decoupled.
if __name__ == '__main__':
    run_parser_by_urls('rabbitmq://localhost:27017/inmymind?q_name=parser_pose&routing_key=parser',
                       'pose://',
                       'rabbitmq://localhost:27017/inmymind?q_name=parser_pose&routing_key=saver')
