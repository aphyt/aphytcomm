__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import binascii


class CipResponse:
    def __init__(self, response_bytes):
        """ Parse Response Bytes

        | Message sequence number   | 2 bytes little endian |
        | Data size                 | 2 bytes little endian |
        | Reserved                  | 1 bytes little endian |
        | Service code              | 1 bytes little endian |
        | General Status            | 1 bytes little endian |
        | Size of additional status | 1 bytes little endian |
        | Data                      | 496 bytes max         |

        :param response_bytes:
        """
        self.message_sequence_number = int.from_bytes(response_bytes[0:2], 'little')
        self.data_size = int.from_bytes(response_bytes[2:4], 'little')
        self.reserved = response_bytes[4:5]
        self.service_code = response_bytes[5:6]
        self.general_status = response_bytes[6:7]
        self.size_of_additional_status = response_bytes[7:8]
        self.data = response_bytes[8:]

    def __repr__(self):
        return 'Message Number: %s contains: %s' % (self.message_sequence_number, binascii.hexlify(self.data))
