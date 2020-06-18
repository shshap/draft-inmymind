import base64
import gzip
import json
import logging
import struct
from pathlib import Path
from urllib.parse import urlparse

from google.protobuf.json_format import MessageToDict

from inmymind.parser._parser_utils import find_parse_method
from inmymind.protocols.mind.cortex_pb2 import Snapshot

logger = logging.getLogger(__name__)

DEFAULT_PARSER_TAG = 'depth_image'


def parser_mind(path: bytes, content_type, parser_url, sender):
    parse = find_parse_method(parser_url)
    data = helper_read_path(path)
    url = urlparse(parser_url)
    parser_tag = url.scheme if url.scheme else DEFAULT_PARSER_TAG
    user_id, = struct.unpack('I', data[:4])
    datetime, = struct.unpack('I', data[4:12])
    snapshot = Snapshot()
    snapshot.ParseFromString(data[12:])
    try:
        result = getattr(snapshot, parser_tag)
    except AttributeError:
        return 2
    dict_result_fields = MessageToDict(result, preserving_proto_field_name=True)
    if parser_tag == 'color_image':
        dict_result_fields['data'] = base64.b64decode(dict_result_fields.pop('data'))
    dict_result = {parser_tag: dict_result_fields, 'user_id': user_id, 'datetime': snapshot.datetime}
    res = json.dumps(parse(dict_result))
    if sender is None:
        return res  # the caller did not give any where to send, so he will get back the result
    return sender(res, 'mind')


def helper_read_path(path: bytes):
    logger.debug("inside wrapper")
    path = path.decode('utf-8')
    file_format = Path(path).suffix
    if file_format == 'gz':
        open_func = gzip.open
    else:
        open_func = open
    with open_func(path, 'rb') as reader:
        logger.debug('file opened in parser')
        data = reader.read()
    return data
