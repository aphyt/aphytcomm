__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import struct

from aphyt.eip import *
from decimal import *


class F4Series:
    def __init__(self):
        super().__init__()
        self.connected_cip_dispatcher = EIPConnectedCIPDispatcher()

    def connect_explicit(self, host):
        self.connected_cip_dispatcher.connect_explicit(host)

    def close_explicit(self):
        self.connected_cip_dispatcher.close_explicit()

    def register_session(self):
        self.connected_cip_dispatcher.register_session()

    def get_control_register(self):
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x01')
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        return reply.reply_data

    def get_camera_status(self):
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x02')
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        return reply.reply_data


