__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import struct

from aphyt.eip import *
from decimal import *


def set_bit(data: bytes, bit_position: int):
    length = len(data)
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = 2**bit_position
    data_int = data_int | mask_int
    result = data_int.to_bytes(length, 'little', signed=False)
    return result


def clear_bit(data: bytes, bit_position: int):
    length = len(data)
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = ~2**bit_position
    data_int = data_int & mask_int
    result = data_int.to_bytes(length, 'little', signed=False)
    return result


def test_bit(data: bytes, bit_position: int):
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = 2**bit_position
    if data_int & mask_int:
        result = True
    else:
        result = False
    return result


def clear_bytes(data: bytes):
    length = len(data)
    data = b'\x00' * length
    return data


class F4Series:
    def __init__(self):
        super().__init__()
        self.connected_cip_dispatcher = EIPConnectedCIPDispatcher()
        self.blank_control = 0b0000000000000000
        self.status = b'\x00\x00'
        self.camera_control_register = b'\x00\x00'

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
        return test_bit(self.status, 0)

    def status_exposure_busy(self):
        return test_bit(self.status, 1)

    def status_acquisition_busy(self):
        return test_bit(self.status, 2)

    def status_trigger_ready(self):
        return test_bit(self.status, 3)

    def status_error(self):
        return test_bit(self.status, 4)

    def status_reset_count_acknowledgement(self):
        return test_bit(self.status, 5)

    def status_execute_command_acknowledgement(self):
        return test_bit(self.status, 7)

    def status_trigger_acknowledgement(self):
        return test_bit(self.status, 8)

    def status_inspection_busy(self):
        return test_bit(self.status, 9)

    def status_inspection_status(self):
        return test_bit(self.status, 10)

    def status_data_valid(self):
        return test_bit(self.status, 11)

    def get_string(self, number: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6c\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        reply_string = str(reply.reply_data[4:], 'utf-8')
        return reply_string

    def set_string(self, number: int, value: str):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6c\x00', instance_id=b'\x01', attribute_id=attribute_id)
        data_length = len(value)
        data = data_length.to_bytes(4, 'little', signed=False)
        data = data + bytes(value, 'utf-8')
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, data)

    def get_bool(self, number: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x68\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        if reply.reply_data == b'\x01\x00':
            return True
        else:
            return False

    def set_bool(self, number: int, value: bool):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x68\x00', instance_id=b'\x01', attribute_id=attribute_id)
        self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        cip_type = CIPBoolean()
        if value:
            cip_type.from_value(True)
        else:
            cip_type.from_value(False)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def get_int(self, number: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x69\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        value = CIPInteger()
        value.data = reply.reply_data
        return value

    def set_int(self, number: int, value: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x69\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPInteger()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def get_long(self, number: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6a\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        value = CIPLongInteger()
        value.data = reply.reply_data
        return value

    def set_long(self, number: int, value: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6a\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPLongInteger()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def get_float(self, number: int):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6b\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        value = CIPReal()
        value.data = reply.reply_data
        return value

    def set_float(self, number: int, value: float):
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6b\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPReal()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def send_command_register(self):
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x01')
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, self.camera_control_register)
        self.camera_control_register = clear_bytes(self.camera_control_register)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, self.camera_control_register)

    def go_online(self):
        self.camera_control_register = set_bit(self.camera_control_register, 0)
        self.send_command_register()

    def go_offline(self):
        self.camera_control_register = set_bit(self.camera_control_register, 1)
        self.send_command_register()

    def reset_error(self):
        self.camera_control_register = set_bit(self.camera_control_register, 4)
        self.send_command_register()

    def reset_count(self):
        self.camera_control_register = set_bit(self.camera_control_register, 5)
        self.send_command_register()

    def execute_command(self):
        self.camera_control_register = set_bit(self.camera_control_register, 7)
        self.send_command_register()

    def trigger_inspection(self):
        self.get_camera_status()
        while not self.status_trigger_ready():
            self.get_camera_status()
        self.camera_control_register = set_bit(self.camera_control_register, 8)
        self.send_command_register()

    def reset_data_valid(self):
        self.camera_control_register = set_bit(self.camera_control_register, 11)
        self.send_command_register()

