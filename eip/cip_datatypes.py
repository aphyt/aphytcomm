__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import struct
from abc import ABC, abstractmethod


class CIPDataType(ABC):
    """

    """

    @staticmethod
    @abstractmethod
    def data_type_code() -> bytes:
        pass

    def __init__(self):
        self._data_type_code = self.data_type_code()
        self.addition_info_length = 0
        self.additional_info = b''
        self.data = b''
        self.size = 0
        self.attribute_id = None

    def bytes(self):
        byte_value = self.data_type_code() + \
                     self.addition_info_length.to_bytes(1, 'little') + \
                     self.additional_info + \
                     self.data
        return byte_value

    def from_bytes(self, bytes_cip_data_type):
        self._data_type_code = bytes_cip_data_type[0:1]
        self.addition_info_length = int.from_bytes(bytes_cip_data_type[1:2], 'little')
        self.additional_info = bytes_cip_data_type[2:2 + self.addition_info_length]
        self.data = bytes_cip_data_type[2 + self.addition_info_length:]

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def from_value(self, value):
        pass


def _update_data_type_dictionary(data_type_dictionary):
    for sub_class in CIPDataType.__subclasses__():
        data_type_dictionary.update({sub_class.data_type_code(): sub_class})


def _get_class_data_type_code(data_type: bytes) -> CIPDataType:
    for sub_class in CIPDataType.__subclasses__():
        if sub_class.data_type_code() == data_type:
            return sub_class()


class CIPBoolean(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = struct.pack("<h", 0)

    @staticmethod
    def data_type_code():
        return b'\xc1'  # (bit)

    def value(self):
        bool_value = int.from_bytes(self.data, 'little')
        if bool_value == 1:
            return True
        else:
            return False

    def from_value(self, value):
        if value:
            self.data = struct.pack("<h", 1)
        else:
            self.data = struct.pack("<h", 0)


class CIPShortInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00'

    @staticmethod
    def data_type_code():
        return b'\xc2'  # (1-byte signed binary)

    def value(self):
        return struct.unpack("<b", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<b", value)


class CIPInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc3'  # (1-word signed binary)

    def value(self):
        return struct.unpack("<h", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<h", value)


class CIPDoubleInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc4'  # (2-word signed binary)

    def value(self):
        return struct.unpack("<l", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<l", value)


class CIPLongInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc5'  # (1-byte signed binary)

    def value(self):
        return struct.unpack("<q", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<q", value)


class CIPUnsignedShortInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00'

    @staticmethod
    def data_type_code():
        return b'\xc6'  # (1-byte unsigned binary)

    def value(self):
        return struct.unpack("<B", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<B", value)


class CIPUnsignedInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc7'  # (1-word unsigned binary)

    def value(self):
        return struct.unpack("<H", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<H", value)


class CIPUnsignedDoubleInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc8'  # (2-word unsigned binary)

    def value(self):
        return struct.unpack("<L", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<L", value)


class CIPUnsignedLongInteger(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xc9'  # (4-word unsigned binary)

    def value(self):
        return struct.unpack("<Q", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<Q", value)


class CIPReal(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xca'  # (2-word floating point)

    def value(self):
        return struct.unpack("<f", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<f", value)


class CIPLongReal(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xcb'  # (4-word floating point)

    def value(self):
        return struct.unpack("<d", self.data)[0]

    def from_value(self, value):
        self.data = struct.pack("<d", value)


class CIPString(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = str("").encode('utf-8')

    @staticmethod
    def data_type_code():
        return b'\xd0'  #

    def value(self):
        return str(self.data, 'utf-8')

    def from_value(self, value):
        byte_value = value.encode('utf-8')
        length_difference = self.size - len(byte_value)
        byte_value += length_difference * b'\x00'
        self.data = byte_value


class CIPByte(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00'

    @staticmethod
    def data_type_code():
        return b'\xd1'

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPWord(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xd2'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPDoubleWord(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xd3'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPLongWord(CIPDataType):
    def __init__(self):
        super().__init__()
        self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    @staticmethod
    def data_type_code():
        return b'\xd4'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPTime(CIPDataType):
    def __init__(self):
        super().__init__()

    @staticmethod
    def data_type_code():
        return b'\xdb'  # (8-byte data)

    def value(self):
        pass

    def from_value(self, value):
        pass


class CIPAbbreviatedStructure(CIPDataType):
    def __init__(self):
        super().__init__()

    @staticmethod
    def data_type_code():
        return b'\xa0'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPStructure(CIPDataType):
    def __init__(self):
        super().__init__()

    @staticmethod
    def data_type_code():
        return b'\xa2'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class CIPArray(CIPDataType):
    def __init__(self,
                 array_data_type,
                 array_data_size,
                 array_dimensions,
                 number_of_elements,
                 start_array_elements):
        super().__init__()
        self.array_data_type = array_data_type
        self.array_data_type_size = array_data_size
        self.array_dimensions = array_dimensions
        self.number_of_elements = number_of_elements
        self.start_array_elements = start_array_elements
        total_size = self.array_data_type_size
        for number in self.number_of_elements:
            total_size = total_size * number
        self.size = total_size
        self._local_cip_data_type_object = _get_class_data_type_code(self.array_data_type)
        self._list_representation = []
        for i in range(self.array_dimensions):
            self._list_representation.append([self._local_cip_data_type_object.value()] * self.number_of_elements[i])

    @staticmethod
    def data_type_code():
        return b'\xa3'  # (1-byte signed binary) signed char

    def value(self):
        for dimension in range(self.array_dimensions):
            for index in range(self.number_of_elements[dimension]):
                start_bytes = dimension + index * self.array_data_type_size
                self._local_cip_data_type_object.data = \
                    self.data[start_bytes:start_bytes + self.array_data_type_size]
                self._list_representation[dimension][index] = self._local_cip_data_type_object.value()
        return self._list_representation

    def from_value(self, value):
        data = b''
        for dimension in range(self.array_dimensions):
            for index in range(self.number_of_elements[dimension]):
                self._local_cip_data_type_object.from_value(
                    value[dimension][index])
                data += self._local_cip_data_type_object.data
        self.data = data


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
