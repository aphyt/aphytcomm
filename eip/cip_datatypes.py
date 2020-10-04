import struct


class CIPDataTypes:
    """
    CIP has a byte that defines the data represented in the message
    """
    CIP_BOOLEAN = b'\xc1'  # (bit)
    CIP_SINT = b'\xc2'  # (1-byte signed binary) signed char
    CIP_INT = b'\xc3'  # (1-word signed binary) short
    CIP_DINT = b'\xc4'  # (2-word signed binary) int
    CIP_LINT = b'\xc5'  # (4-word signed binary) long long
    CIP_USINT = b'\xc6'  # (1-byte unsigned binary)
    CIP_UINT = b'\xc7'  # (1-word unsigned binary)
    CIP_UDINT = b'\xc8'  # (2-word unsigned binary)
    CIP_ULINT = b'\xc9'  # (4-word unsigned binary)
    CIP_REAL = b'\xca'  # (2-word floating point)
    CIP_LREAL = b'\xcb'  # (4-word floating point)
    CIP_STRING = b'\xd0'
    CIP_BYTE = b'\xd1'  # (1-byte hexadecimal)
    CIP_WORD = b'\xd2'  # (1-word hexadecimal)
    CIP_DWORD = b'\xd3'  # (2-word hexadecimal)
    CIP_TIME = b'\xdb'  # (8-byte data)
    CIP_LWORD = b'\xd4'  # (4-word hexadecimal)
    CIP_ABBREVIATED_STRUCT = b'\xa0'
    CIP_STRUCT = b'\xa2'
    CIP_ARRAY = b'\xa3'
    OMRON_UINT_BCD = b'\x04'  # (1-word unsigned BCD)
    OMRON_UDINT_BCD = b'\x05'  # (2-word unsigned BCD)
    OMRON_ULINT_BCD = b'\x06'  # (4-word unsigned BCD)
    OMRON_ENUM = b'\x07'
    OMRON_DATE_NSEC = b'\x08'
    OMRON_TIME_NSEC = b'\x09'
    OMRON_DATE_AND_TIME_NSEC = b'\x0a'
    OMRON_TIME_OF_DAY_NSEC = b'\x0b'
    OMRON_UNION = b'\x0c'

    def __init__(self):
        self.data_type_code = b''
        self.addition_info_length = 0
        self.additional_info = b''
        self.data = b''

    def bytes(self):
        byte_value = self.data_type_code + \
                     self.addition_info_length.to_bytes(1, 'little') + \
                     self.additional_info + \
                     self.data
        return byte_value

    def from_bytes(self, bytes_cip_data_type):
        self.data_type_code = bytes_cip_data_type[0:1]
        self.addition_info_length = int.from_bytes(bytes_cip_data_type[1:2], 'little')
        self.additional_info = bytes_cip_data_type[2:2 + self.addition_info_length]
        self.data = bytes_cip_data_type[2 + self.addition_info_length:]

    def value(self):
        if self.data_type_code == CIPDataTypes.CIP_BOOLEAN:
            bool_value = int.from_bytes(self.data, 'little')
            if bool_value == 1:
                return True
            else:
                return False
        elif self.data_type_code == CIPDataTypes.CIP_SINT:
            return struct.unpack("<b", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_INT:
            return struct.unpack("<h", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_DINT:
            return struct.unpack("<l", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_LINT:
            return struct.unpack("<q", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_USINT:
            return struct.unpack("<B", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_UINT:
            return struct.unpack("<H", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_UDINT:
            return struct.unpack("<L", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_ULINT:
            return struct.unpack("<Q", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_REAL:
            return struct.unpack("<f", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_LREAL:
            return struct.unpack("<d", self.data)[0]
        elif self.data_type_code == CIPDataTypes.CIP_STRING:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_WORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_DWORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_TIME:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_LWORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_ABBREVIATED_STRUCT:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_STRUCT:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_ARRAY:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UDINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_ULINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_ENUM:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_DATE_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_TIME_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_DATE_AND_TIME_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_TIME_OF_DAY_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UNION:
            pass

    def from_value(self, value, data_type_code: bytes, additional_info: bytes):
        self.data_type_code = data_type_code
        self.addition_info_length = len(additional_info)
        self.additional_info = additional_info
        if self.data_type_code == CIPDataTypes.CIP_BOOLEAN:
            if value:
                self.data = struct.pack("<h", 1)
            else:
                self.data = struct.pack("<h", 0)
        elif self.data_type_code == CIPDataTypes.CIP_SINT:
            self.data = struct.pack("<b", value)
        elif self.data_type_code == CIPDataTypes.CIP_INT:
            self.data = struct.pack("<h", value)
        elif self.data_type_code == CIPDataTypes.CIP_DINT:
            self.data = struct.pack("<l", value)
        elif self.data_type_code == CIPDataTypes.CIP_LINT:
            self.data = struct.pack("<q", value)
        elif self.data_type_code == CIPDataTypes.CIP_USINT:
            self.data = struct.pack("<B", value)
        elif self.data_type_code == CIPDataTypes.CIP_UINT:
            self.data = struct.pack("<H", value)
        elif self.data_type_code == CIPDataTypes.CIP_UDINT:
            self.data = struct.pack("<L", value)
        elif self.data_type_code == CIPDataTypes.CIP_ULINT:
            self.data = struct.pack("<Q", value)
        elif self.data_type_code == CIPDataTypes.CIP_REAL:
            self.data = struct.pack("<f", value)
        elif self.data_type_code == CIPDataTypes.CIP_LREAL:
            self.data = struct.pack("<d", value)
        elif self.data_type_code == CIPDataTypes.CIP_STRING:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_WORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_DWORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_TIME:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_LWORD:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_ABBREVIATED_STRUCT:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_STRUCT:
            pass
        elif self.data_type_code == CIPDataTypes.CIP_ARRAY:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UDINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_ULINT_BCD:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_ENUM:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_DATE_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_TIME_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_DATE_AND_TIME_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_TIME_OF_DAY_NSEC:
            pass
        elif self.data_type_code == CIPDataTypes.OMRON_UNION:
            pass