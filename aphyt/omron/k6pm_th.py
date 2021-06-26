__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.eip import *


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
