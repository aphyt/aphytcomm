__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import struct

from aphyt.eip import *
from decimal import *


class V4_SERIES:
    def __init__(self):
        super().__init__()
        self.connected_cip_dispatcher = EIPConnectedCIPDispatcher()
        self.last_read_length = 0
        self.last_read_string = ''

    def connect_explicit(self, host):
        # ToDo Consider moving all these convenience methods to a Mixin
        self.connected_cip_dispatcher.connect_explicit(host)

    def close_explicit(self):
        self.connected_cip_dispatcher.close_explicit()

    def register_session(self):
        self.connected_cip_dispatcher.register_session()

    def execute_command(self, command) -> bytes:
        service_code = b'\x45'
        request_path = address_request_path_segment(class_id=b'\x68\x00', instance_id=b'\x01', attribute_id=b'\x01')
        data = struct.pack('<I', len(command))
        data = data + bytes(command, 'utf-8')
        request = CIPRequest(service_code, request_path, request_data=data)
        reply = self.connected_cip_dispatcher.execute_cip_command(request)
        return reply.reply_data

    def read_execute(self, delimiter=' '):
        command = '<' + delimiter + '>'
        reply = self.execute_command(command)
        length = struct.unpack('<I', reply[0:4])[0]
        self.last_read_length = length
        self.last_read_string = str(reply[4:], 'utf-8')
        return self.last_read_string





