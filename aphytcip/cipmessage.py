__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


class CipMessage:
    def __init__(self, service_code, class_id, instance_id, attribute_id, data, sequence_number):
        self.reserved_byte_1 = b'\x00\x00'
        self.reserved_byte_2 = b'\x00'
        self.command = self.reserved_byte_2 + service_code + class_id + instance_id
        if attribute_id != b'\x00':
            self.command += attribute_id
        self.command += data
        self.command_length_bytes = len(data)
        self.command = sequence_number.to_bytes(2, 'little') + self.reserved_byte_1 + \
                       self.command_length_bytes + self.command
