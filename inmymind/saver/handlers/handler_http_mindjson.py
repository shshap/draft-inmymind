import logging
import json
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


DEFAULT_HOST_HTTP = '127.0.0.1'
DEFAULT_PORT_HTTP = 5001


class Handler_http_mindjson:
    def __init__(self, raw_url):
        url = urlparse(raw_url)
        self.host = url.hostname if url.hostname else DEFAULT_HOST_HTTP
        self.port = url.port if url.port else DEFAULT_PORT_HTTP
        self.queries = {attr.split('=')[0]: attr.split('=')[1] for attr in url.query.split('&')}

    def handle_message(self, message, content_type):
        msg_type = content_type.split('/')[1]
        try:
            if msg_type == 'user':
                return self.handle_user(message['data'])
            elif msg_type == 'snapshot':
                return self.handle_snapshot(message['data'])
            else:
                logger.warning("message type {msg_type} is not supported")
                return 2
        except ConnectionError:
            logger.debug('catched connection refused')
            return 1

    def handle_user(self, data_user):
        logger.debug("Handling user...")
        dict_user = json.loads(data_user)
        logger.debug('dict_user of type %r and content %r' % (type(dict_user), dict))
        r_post = self._post_user(dict_user)
        logger.debug('got status code from post: %d' % r_post.status_code)
        if r_post.status_code == 201:
            logger.debug('user created successfully')
            return 0
        if r_post.status_code == 409:
            r_put = self._put_user(dict_user)
            if r_put.status_code == 200:
                return 0
            else:
                logger.warning(r_put.text)
                return 2
        else:
            logger.warning(r_post.text)
            return 2

    def _post_user(self, dict_user):
        logger.debug(f"send post request for user {dict_user}")
        return requests.post(path + '/users/',
                             data=json.dumps({'user': dict_user}),
                             headers={'Content-type': 'application/json'})

    def _put_user(self, dict_user):
        logger.debug(f"send put request for user {dict_user}")
        user_id = dict_user['user_id']
        return requests.put(path + f'/users/{user_id}/',
                            data=json.dumps({'user': dict_user}),
                            headers={'Content-type': 'application/json'})

    def handle_snapshot(self, data_snap):
        logger.debug("Handling snapshot...")
        dict_snap = json.loads(data_snap)
        r_post = self._post_snapshot(dict_snap)
        logger.debug('got status code from post: %d' % r_post.status_code)
        if r_post.status_code == 201:
            logger.debug('snapshot created successfully')
            return 0
        elif r_post.status_code == 409:
            snap_id = r_post.json()
            logger.debug(f'snap_id for put is {snap_id} of type {type(snap_id)}')
            r_put = self._put_snapshot(dict_snap, snap_id)
            logger.debug(f'got r_put {r_put}')
            if r_put.status_code == 200:
                return 0
            else:
                logger.warning(r_put.text)
                return 2
        else:
            logger.warning(r_post.text)
            return 2

    # the form of dict_snap is {'user_id': 21, 'username: Amit, '<field>': {...}, '<field>': {...}}
    def _post_snapshot(self, dict_snap):
        logger.debug(f"send post request for snap {dict_snap['user_id']}")
        user_id = dict_snap['user_id']
        return requests.post(path + f'/users/{user_id}/snapshots/',
                             data=json.dumps({'snapshot': dict_snap}),
                             headers={'Content-type': 'application/json'})

    def _put_snapshot(self, dict_snap, snap_id):
        logger.debug(f"send put request for snap {dict_snap['user_id']}")
        user_id = dict_snap['user_id']
        return requests.put(path + f'/users/{user_id}/snapshots/{snap_id}/',
                            data=json.dumps({'snapshot': dict_snap}),
                            headers={'Content-type': 'application/json'})
