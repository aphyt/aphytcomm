__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.eip import *


def set_bit(data: bytes, bit_position: int):
    """Set an arbitrary bit in a bytes object to 1"""
    length = len(data)
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = 2**bit_position
    data_int = data_int | mask_int
    result = data_int.to_bytes(length, 'little', signed=False)
    return result


def clear_bit(data: bytes, bit_position: int):
    """Set an arbitrary bit in a bytes object to 0"""
    length = len(data)
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = ~2**bit_position
    data_int = data_int & mask_int
    result = data_int.to_bytes(length, 'little', signed=False)
    return result


def test_bit(data: bytes, bit_position: int):
    """Determine if an arbitrary bit in a bytes object is 1 or 0"""
    data_int = int.from_bytes(data, 'little', signed=False)
    mask_int = 2**bit_position
    if data_int & mask_int:
        result = True
    else:
        result = False
    return result


def clear_bytes(data: bytes):
    """Set bytes object to all 0"""
    length = len(data)
    data = b'\x00' * length
    return data


class F4Series:
    """
    F4Series
    ~~~~~~~

    Class that implements Omron F4 vision sensor specific Ethernet/IP services
    """
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
        """
        Method to request the current content of the control register
        :return:
        """
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x01')
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        return reply.reply_data

    def get_camera_status(self):
        """
        Method to request status register from the camera. This method should be executed prior to using the status
        methods.
        :return:
        """
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x02')
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        self.status = reply.reply_data
        return self.status

    def status_online(self):
        """Returns true if the status register reports that inspections are running"""
        return test_bit(self.status, 0)

    def status_exposure_busy(self):
        """
        Returns true if the status register reports that the camera is capturing an image. For F440-F it is
        equivalent to acquisition busy
        """
        return test_bit(self.status, 1)

    def status_acquisition_busy(self):
        """Returns true if the status register reports that the camera is acquiring an image"""
        return test_bit(self.status, 2)

    def status_trigger_ready(self):
        """Returns true if the status register reports that the camera is ready to be triggered"""
        return test_bit(self.status, 3)

    def status_error(self):
        """
        Returns true if the status register reports an error has occurred. Set the reset error
        control bit in the command register to reset.
        """
        return test_bit(self.status, 4)

    def status_reset_count_acknowledgement(self):
        """Returns true if the status register reports that the reset count signal was received"""
        return test_bit(self.status, 5)

    def status_execute_command_acknowledgement(self):
        """Returns true if the status register reports that the execute command signal was received"""
        return test_bit(self.status, 7)

    def status_trigger_acknowledgement(self):
        """Returns true if the status register reports the trigger signal was received"""
        return test_bit(self.status, 8)

    def status_inspection_busy(self):
        """Returns true if the status register reports the inspection is busy processing an image"""
        return test_bit(self.status, 9)

    def status_inspection_status(self):
        """
        Returns true if the status register reports the inspection has passed. It is only valid
        when the DataValid bit is high.
        """
        return test_bit(self.status, 10)

    def status_data_valid(self):
        """
        Returns true if the status register reports the inspection 1 is complete. The controller
        should clear this signal by setting the reset data valid once results have been read.
        """
        return test_bit(self.status, 11)

    def get_string(self, number: int):
        """Get the string stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6c\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        reply_string = str(reply.reply_data[4:], 'utf-8')
        return reply_string

    def set_string(self, number: int, value: str):
        """Set the string stored in the camera at the specified attribute number"""
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
        """Get the Boolean stored in the camera at the specified attribute number"""
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
        """Set the Boolean stored in the camera at the specified attribute number"""
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
        """Get the 16-bit Integer stored in the camera at the specified attribute number"""
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
        """Set the 16-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x69\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPInteger()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def get_long(self, number: int):
        """Get the 32-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6a\x00', instance_id=b'\x01', attribute_id=attribute_id)
        reply = self.connected_cip_dispatcher.get_attribute_single_service(request_path)
        value = CIPDoubleInteger()
        value.data = reply.reply_data
        return value

    def set_long(self, number: int, value: int):
        """Set the 32-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6a\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPDoubleInteger()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def get_float(self, number: int):
        """Get the Floating Point stored in the camera at the specified attribute number"""
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
        """Set the Floating Point stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        attribute_id = number.to_bytes(2, 'little', signed=False)
        request_path = address_request_path_segment(
            class_id=b'\x6b\x00', instance_id=b'\x01', attribute_id=attribute_id)
        cip_type = CIPReal()
        cip_type.from_value(value)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, cip_type.data)

    def send_command_register(self):
        """Send the command register to the camera to execute the control bits that are set"""
        request_path = address_request_path_segment(class_id=b'\x6d\x00', instance_id=b'\x01', attribute_id=b'\x01')
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, self.camera_control_register)
        self.camera_control_register = clear_bytes(self.camera_control_register)
        self.connected_cip_dispatcher.set_attribute_single_service(request_path, self.camera_control_register)

    def go_online(self):
        """Start all inspections running"""
        self.camera_control_register = set_bit(self.camera_control_register, 0)
        self.send_command_register()

    def go_offline(self):
        """Stop all inspections"""
        self.camera_control_register = set_bit(self.camera_control_register, 1)
        self.send_command_register()

    def reset_error(self):
        """Reset error in the status register"""
        self.camera_control_register = set_bit(self.camera_control_register, 4)
        self.send_command_register()

    def reset_count(self):
        """Reset all inspection counts"""
        self.camera_control_register = set_bit(self.camera_control_register, 5)
        self.send_command_register()

    def execute_command(self):
        """Execute command specified by Control.CmdCode"""
        self.camera_control_register = set_bit(self.camera_control_register, 7)
        self.send_command_register()

    def trigger_inspection(self):
        """Trigger inspection 1. The inspection must be configured for  triggered image acquisition"""
        self.get_camera_status()
        while not self.status_trigger_ready():
            self.get_camera_status()
        self.camera_control_register = set_bit(self.camera_control_register, 8)
        self.send_command_register()

    def reset_data_valid(self):
        """
        Reset the Data Valid signal of the status register.
        This should be performed after the data has been read.
        """
        self.camera_control_register = set_bit(self.camera_control_register, 11)
        self.send_command_register()

