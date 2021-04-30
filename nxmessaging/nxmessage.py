__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


class CipMessage:
    def __init__(self, service_code, class_id, instance_id, attribute_id, sequence_number, data=b''):
        """ Assemble as CIP Message

        | Message sequence number | 2 bytes little endian |
        | Reserved 1              | 2 bytes little endian |
        | Data size               | 2 bytes little endian |
        | Reserved 2              | 1 bytes little endian |
        | Service code            | 1 bytes little endian |
        | Class ID                | 2 bytes little endian |
        | Instance ID             | 2 bytes little endian |
        | Attribute ID            | 2 bytes little endian |
        | Data                    | 490 bytes max         |

        :param service_code:
        :param class_id:
        :param instance_id:
        :param attribute_id:
        :param sequence_number:
        :param data:
        """
        self.reserved_byte_1 = b'\x00\x00'
        self.reserved_byte_2 = b'\x00'
        self.command = self.reserved_byte_2 + service_code + class_id + instance_id + attribute_id
        self.command += data
        self.command_length_bytes = len(self.command).to_bytes(2, 'little')
        self.command = sequence_number.to_bytes(2, 'little') + self.reserved_byte_1 + \
                       self.command_length_bytes + self.command
