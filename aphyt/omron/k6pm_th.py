__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.eip import *
from decimal import *

class CIPService:
    def __init__(self):
        class_id = None


class K6PMTHEIP(EIP):
    """
    CIP Class ID


    """
    def __init__(self):
        super().__init__()

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
        internal_temperature = CIPUnsignedInteger()
        internal_temperature.data = self.get_attribute_single_service(read_address).reply_data
        internal_temperature = Decimal(internal_temperature.value())/Decimal(10.0)
        return internal_temperature

    def internal_maximum_temperature(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x68')
        internal_maximum_temperature = CIPUnsignedInteger()
        internal_maximum_temperature.data = self.get_attribute_single_service(read_address).reply_data
        internal_maximum_temperature = Decimal(internal_maximum_temperature.value()) / Decimal(10.0)
        return internal_maximum_temperature

    def internal_predicted_arrival(self, sensor_number: int):
        instance_id = struct.pack("<B", sensor_number)
        read_address = address_request_path_segment(class_id=b'\x75\x03', instance_id=instance_id, attribute_id=b'\x69')
        internal_predicted_arrival = CIPUnsignedInteger()
        internal_predicted_arrival.data = self.get_attribute_single_service(read_address).reply_data
        internal_predicted_arrival = Decimal(internal_predicted_arrival.value()) / Decimal(10.0)
        return internal_predicted_arrival
