__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.eip import *
from decimal import *


def two_bytes_to_fixed_point_temperature(two_bytes: bytes):
    temperature = struct.unpack("<H", two_bytes)[0]
    temperature = Decimal(temperature) / Decimal(10.0)
    return temperature


def two_bytes_to_uint(two_bytes: bytes):
    uint_instance = struct.unpack("<H", two_bytes)[0]
    uint_instance = Decimal(uint_instance) / Decimal(10.0)
    return uint_instance


def unsigned_integer_to_temp(unsigned: int):
    temperature = Decimal(unsigned) / Decimal(10.0)
    return temperature


class SensorMonitorObject:
    def __init__(self):
        self.sensor_version = None
        self.sensor_status = None
        self.alarm_status = None
        self.internal_temperature_value = None
        self.internal_max_temperature_value = None
        self.internal_predicted_arrival_time = None
        self.segment_temperature_list = [None] * 16
        self.segment_max_temperature_list = [None] * 16
        self.segment_predicted_temperature = [None] * 16
        self._temp_list_offset = 12
        self._max_temp_list_offset = self._temp_list_offset + 16
        self._predicted_temp_list_offset = self._max_temp_list_offset

    def from_bytes(self, sensor_monitor_attributes_bytes: bytes):
        self.sensor_version = two_bytes_to_uint(sensor_monitor_attributes_bytes[0:2])
        self.sensor_status = two_bytes_to_uint(sensor_monitor_attributes_bytes[2:4])
        self.alarm_status = two_bytes_to_uint(sensor_monitor_attributes_bytes[4:6])
        self.internal_temperature_value = two_bytes_to_fixed_point_temperature(sensor_monitor_attributes_bytes[6:8])
        self.internal_max_temperature_value = \
            two_bytes_to_fixed_point_temperature(sensor_monitor_attributes_bytes[8:10])
        self.internal_predicted_arrival_time = \
            two_bytes_to_fixed_point_temperature(sensor_monitor_attributes_bytes[10:12])
        for i in range(16):
            t_start = i*2 + self._temp_list_offset
            mt_start = i*2 + self._max_temp_list_offset
            pt_start = i*2 + self._predicted_temp_list_offset
            temp_bytes = \
                sensor_monitor_attributes_bytes[t_start:t_start+2]
            self.segment_temperature_list[i] = two_bytes_to_fixed_point_temperature(temp_bytes)
            max_bytes = \
                sensor_monitor_attributes_bytes[mt_start:mt_start+2]
            self.segment_max_temperature_list[i] = two_bytes_to_fixed_point_temperature(max_bytes)
            predict_bytes = \
                sensor_monitor_attributes_bytes[pt_start:pt_start+2]
            self.segment_predicted_temperature[i] = two_bytes_to_fixed_point_temperature(predict_bytes)


class K6PMTHEIP(EIPConnectedCIPDispatcher):
    """
    CIP Class ID


    """
    def __init__(self):
        super().__init__()

    def get_attribute_single_as_uint(self, read_address: address_request_path_segment):
        cip_unsigned_integer = CIPUnsignedInteger()
        cip_unsigned_integer.data = self.get_attribute_single_service(read_address).reply_data
        return cip_unsigned_integer.value()

    def get_attribute_single_as_temp(self, read_address: address_request_path_segment):
        cip_unsigned_integer = CIPUnsignedInteger()
        cip_unsigned_integer.data = self.get_attribute_single_service(read_address).reply_data
        temperature = Decimal(cip_unsigned_integer.value()) / Decimal(10.0)
        return temperature

    def main_unit_status(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x64')
        main_unit_status = CIPUnsignedInteger()
        main_unit_status.data = self.get_attribute_single_service(read_address).reply_data
        return main_unit_status

    def running_time(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x65')
        running_time = CIPUnsignedInteger()
        running_time.data = self.get_attribute_single_service(read_address).reply_data
        return running_time

    def software_version(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x66')
        software_version = CIPUnsignedInteger()
        software_version.data = self.get_attribute_single_service(read_address).reply_data
        return software_version

    def number_of_connected_sensors(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x67')
        sensor_count = CIPUnsignedInteger()
        sensor_count.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_count
    
    def sensor_in_position_adjustment_mode(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x68')
        sensor_in_position_adjustment_mode = CIPUnsignedInteger()
        sensor_in_position_adjustment_mode.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_in_position_adjustment_mode

    def sensor_monitor_object(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id)
        sensor_monitor_object = SensorMonitorObject()
        sensor_monitor_object.from_bytes(self.get_attribute_all_service(read_address).reply_data)
        return sensor_monitor_object

    def sensor_version(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x64')
        sensor_version = CIPUnsignedInteger()
        sensor_version.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_version

    def sensor_status(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x65')
        sensor_status = CIPUnsignedInteger()
        sensor_status.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_status

    def sensor_alarm_status(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x66')
        sensor_alarm_status = CIPUnsignedInteger()
        sensor_alarm_status.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_alarm_status

    def internal_temperature(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x67')
        return self.get_attribute_single_as_temp(read_address)

    def internal_maximum_temperature(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x68')
        return self.get_attribute_single_as_temp(read_address)

    def internal_predicted_arrival(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x69')
        return self.get_attribute_single_as_temp(read_address)

    def segment_temp_current(self, sensor_number: int, segment_number: int):
        instance_id = struct.pack("<B", sensor_number)
        attribute_id = struct.pack("<B", segment_number + 0x6a)
        read_address = address_request_path_segment(
            class_id=b'\x75\x03', instance_id=instance_id, attribute_id=attribute_id)
        return self.get_attribute_single_as_temp(read_address)

    def segment_temp_max(self, sensor_number: int, segment_number: int):
        instance_id = struct.pack("<B", sensor_number)
        attribute_id = struct.pack("<B", segment_number + 0x7a)
        read_address = address_request_path_segment(
            class_id=b'\x75\x03', instance_id=instance_id, attribute_id=attribute_id)
        return self.get_attribute_single_as_temp(read_address)

    def segment_temp_predicted(self, sensor_number: int, segment_number: int):
        instance_id = struct.pack("<B", sensor_number)
        attribute_id = struct.pack("<B", segment_number + 0x8a)
        read_address = address_request_path_segment(
            class_id=b'\x75\x03', instance_id=instance_id, attribute_id=attribute_id)
        return self.get_attribute_single_as_temp(read_address)

    def pixel_temperatures(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        temporary_array = CIPArray()
        temp_instance = CIPUnsignedInteger()
        temporary_array.from_instance(temp_instance, temp_instance.size, 1, [64], [0])
        result_array = []
        for i in range(16):
            attribute_id = struct.pack("<B", i + 0x64)
            read_address = address_request_path_segment(
                class_id=b'\x76\x03', instance_id=instance_id, attribute_id=attribute_id)
            temporary_array.data = self.get_attribute_single_service(read_address).reply_data
            result_array.append(temporary_array.value())
        return result_array
