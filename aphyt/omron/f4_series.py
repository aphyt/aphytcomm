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
        self.blank_control = 0b0000000000000000
        self.status = 0b0000000000000000
        self.camera_control_register = 0b0000000000000000

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
        self.status = reply.reply_data
        return self.status

    def status_online(self):
        if 0b0000000000000001 & int.from_bytes(self.status, 'little'):
            return True
        else:
            return False

    def trigger_inspection(self):
        self.camera_control_register = 0b0000000100000000 | self.camera_control_register
        register_bytes = self.camera_control_register.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x01')
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, register_bytes)
        self.camera_control_register = self.blank_control
        register_bytes = self.camera_control_register.to_bytes(2, 'little', signed=False)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, register_bytes)



