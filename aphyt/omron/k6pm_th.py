__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.eip import *


class K6PMTHEIP(EIP):
    def __init__(self):
        super().__init__()

    def number_of_connected_sensors(self):
        read_address = address_request_path_segment(class_id=b'\x74\x03', instance_id=b'\x01', attribute_id=b'\x67')
        sensor_count = CIPUnsignedInteger()
        sensor_count.data = self.get_attribute_single_service(read_address).reply_data
        return sensor_count
