import struct


def address_request_path_segment(class_id: bytes = None, instance_id: bytes = None,
                                 attribute_id: bytes = None, element_id: bytes = None) -> bytes:
    """

    :param class_id: class id with low byte first
    :param instance_id:
    :param attribute_id:
    :param element_id
    :return:
    """
    # Logical segment  1756-pm020 16 of 94
    request_path_bytes = b''
    if class_id is not None:
        # 8-bit id uses b'\x20 16-bit uses b'\x21'
        if len(class_id) == 1:
            request_path_bytes += b'\x20' + class_id
        elif len(class_id) == 2:
            request_path_bytes += b'\x21\x00' + class_id
    if instance_id is not None:
        # 8-bit id uses b'\x24' 16-bit uses b'\x25'
        if len(instance_id) == 1:
            request_path_bytes += b'\x24' + instance_id
        elif len(instance_id) == 2:
            request_path_bytes += b'\x25\x00' + instance_id
    if attribute_id is not None:
        # 8-bit id uses b'\x30' 16-bit uses b'\x31'
        if len(attribute_id) == 1:
            request_path_bytes += b'\x30' + attribute_id
        elif len(attribute_id) == 2:
            request_path_bytes += b'\x31\x00' + attribute_id
    if element_id is not None:
        # 8-bit id uses b'\x28' 16-bit uses b'\x29' 32-bit uses b'\x2a'
        if len(element_id) == 1:
            request_path_bytes += b'\x28' + element_id
        elif len(element_id) == 2:
            request_path_bytes += b'\x29\x00' + element_id
        elif len(element_id) == 4:
            request_path_bytes += b'\x2a\x00' + element_id
    return request_path_bytes


def variable_request_path_segment(variable_name: str) -> bytes:
    """
    This static method returns a variable name to a symbolic segment request path.
    :param variable_name: The name of the variable for the request path
    :return: Request path as a bytes object
    """
    # Symbolic segment
    # 1756-pm020_-en-p.pdf 17 of 94
    request_path_bytes = b'\x91' + len(variable_name).to_bytes(1, 'little') + variable_name.encode('utf-8')
    if len(request_path_bytes) % 2 != 0:
        request_path_bytes = request_path_bytes + b'\x00'
    return request_path_bytes


class CIPRequest:
    """
    Class for assembling CIP requests

    ``1756-pm020_-en-p.pdf 17 of 94``

    * Read Tag Service (0x4c)
    * Read Tag Fragmented Service (0x52)
    * Write Tag Service (0x4d)
    * Write Tag Fragmented Service (0x53)
    * Read Modify Write Tag Service (0x4e)

    """
    READ_TAG_SERVICE = b'\x4c'
    READ_TAG_FRAGMENTED_SERVICE = b'\x52'
    WRITE_TAG_SERVICE = b'\x4d'
    WRITE_TAG_FRAGMENTED_SERVICE = b'\x53'
    READ_MODIFY_WRITE_TAG_SERVICE = b'\x4e'
    # w506_nx_nj - series_cpu_unit_built - in_ethernet_ip_port_users_manual_en.pdf
    # 303 of 570 CIP Object Services
    GET_ATTRIBUTE_ALL = b'\x01'
    GET_ATTRIBUTE_SINGLE = b'\x0e'
    RESET = b'\x05'
    SET_ATTRIBUTE_SINGLE = b'\x10'

    def __init__(self,
                 request_service: bytes,
                 request_path: bytes,
                 request_data: bytes = b''):
        """ Constructor method

        :param request_service: bytes
        :param request_path: bytes
        :param request_data: bytes
        """
        self.request_service = request_service
        self.request_data = request_data
        # Length is in Words, so the byte length is divided in half
        self.request_path_size = len(request_path) // 2
        self.request_path = request_path

    def bytes(self) -> bytes:
        """

        :return:
        """
        return self.request_service + self.request_path_size.to_bytes(1, 'little') + \
               self.request_path + self.request_data


class CIPReply:
    """
    Class for parsing CIP replies
    """

    def __init__(self, reply_bytes: bytes):
        """

        :param reply_bytes:
        """
        self.reply_service = reply_bytes[0:1]
        self.reserved = reply_bytes[1:2]
        self.general_status = reply_bytes[2:3]
        self.extended_status_size = reply_bytes[3:4]
        # Research replies that use this. It's usually zero, so I am guessing it is in words (like the request)
        extended_status_byte_offset = int.from_bytes(self.extended_status_size, 'little') * 2
        self.extended_status = reply_bytes[4:extended_status_byte_offset]
        self.reply_data = reply_bytes[4 + extended_status_byte_offset:]

    def bytes(self):
        """
        The bytes in the CIP reply
        :return:
        """
        return self.reply_service + self.reserved + self.general_status + self.extended_status_size + \
               self.extended_status + self.reply_data


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


class CIPCommonFormat:
    """
    Look at W506 page 341 of 570 for definition
    """

    def __init__(self,
                 data_type: bytes = b'',
                 additional_info_length: int = 0,
                 additional_info: bytes = b'',
                 data: bytes = b''):
        self.data_type = data_type
        self.additional_info_length = additional_info_length
        self.additional_info = additional_info
        self.data = data

    def from_bytes(self, bytes_cip_common_format):
        self.data_type = bytes_cip_common_format.reply_data[0:1]
        self.additional_info_length = int.from_bytes(bytes_cip_common_format.reply_data[1:2], 'little')
        self.additional_info = bytes_cip_common_format.reply_data[2:2 + self.additional_info_length]
        self.data = bytes_cip_common_format[2 + self.additional_info_length:]

    def to_value(self):
        # ToDo use data type to display the value rationally
        pass
