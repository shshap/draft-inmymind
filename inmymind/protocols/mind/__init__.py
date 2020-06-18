"""
protocols: Determines what is the format of the content the each component forwards to next one.
    It is totally decoupled from the mechanism of the system.
    To use a new protocol:
    1. Decide what is the sample format
    2. Decide what content will be passed in each stage, for the user and for the snapshot.
    3. Give it an explicit name. Use this name for the functions/classes names and for the content type in the messages.
    4. Just drop your code in the subpackges, the platform knows to find them.
    5. Done! run the system with the urls discovers your protocol. Enjoy :)

    Protocols in use:
    -**Default**: ``Mind`` protocol: uses protobuf, ``.proto`` file: :mod:`cortex.proto`
        * *Sample*: uint32 of the user size and then the `user`, and then for each snapshot: uint32 of snapshot size and
        then the `snapshot`.
        * *Client to server*: for user data: ``data=serialized user`` and ``content_type=mind/user``.
        For snapshot data: ``data=raw user id(int) + raw datetime(long) + serialized snapshots`` ``content_type=mind/snapshot``.
        * *Server to saver*: forwards user data:``data=parsed user in dict type`` and ``content_type=mind/user``, sent in json format.
        * *server to parsers*: forwards snapshots data: path to a .mind.gz file contains the snapshots data it got from the client.
        * *Parsers to saver*: parsed snapshot, in dict type with the keys ``user_id``, ``datetime``, ``<result name>``.
          result name's value is depends on the result name: ``pose`` and ``feelings`` will be the parsed messages,
         ``color_image`` and ``depth_image`` will be a path to the saved image. The dict is sent in json format.
        * *Saver to API*: send exactly what he got from the server and the parsers.

Reader in Mind protocol:
dict of the following form: ``{'data': item, 'content_type': <item_format>/<item_name>}``.
    For example: ``{'data': <raw_user_in_mind_format>, 'content_type': 'mind'}``




"""