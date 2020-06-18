"""
The job of the Client's reader job is to read the sample, to proccess the content, and to output the result
to be sent to the next component, following the protocol .
Reads item by item, using the driver and outputs the items one by one.
The input format is interfered from the driver_url in the upload_sample_by_urls function,
in client.py, if possible, otherwise it will be ``Mind`` protocol.
"""
import json
import logging
import struct

from google.protobuf.json_format import MessageToDict

from inmymind.protocols.mind.cortex_pb2 import Snapshot, User

logger = logging.getLogger(__name__)


def reader_example(url, driver):
    """
    reader is a function. If ones prefers a class, it has a ``read`` function with the same signature, and
    to the __init__ function must get the reader_url.
    Reader's name must be reader_*protocol*. Here, the protocol is 'example'.
    The output format is a dict contains the keys: ``data`` and ``content_type``.
    The specific values are described in the relevant protocol.

    The Client's reader, must be in the `readers subdirectory` of ``client subpackge``
    (as a separate module ot in an existing module).
    """


def reader_mind(driver):
    """Client's reader that handles data in Mind protocol"""
    logger.debug('in reader_mind_mind start')
    try:
        logger.debug('in reader_mind_mind going to read size')
        raw_user_size = driver.read(4)
        if raw_user_size == b'':
            print("File is empty, Job is done")
            yield None
        user_size, = struct.unpack('I', raw_user_size)
        user = User()
        user.ParseFromString(driver.read(user_size))
        dict_user = MessageToDict(user, preserving_proto_field_name=True, use_integers_for_enums=True)
        dict_user['user_id'] = int(dict_user.pop('user_id'))
        yield {'data': json.dumps(dict_user), 'content_type': 'mind/user'}

        logger.debug('start reading snapshots')
        raw_user_id = struct.pack('I', user.user_id)
        while True:
            logger.debug('in reader_mind_mind going to read snapshot')
            raw_snap_size = driver.read(4)
            if raw_snap_size == b'':
                print("Done reading snapshots")
                yield None
            snap_size, = struct.unpack('I', raw_snap_size)
            raw_snapshot = driver.read(snap_size)
            snap = Snapshot()
            snap.ParseFromString(raw_snapshot)
            logger.debug(f'{snap.datetime=}')
            raw_datetime = struct.pack('L', snap.datetime)
            yield {'data': raw_user_id + raw_datetime + raw_snapshot,
                   'content_type': 'mind/snapshot'}
            logger.debug('going to yield None')
            yield None
    except TypeError:
        raise TypeError("The given file has not the right form")
