__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from abc import ABC, abstractmethod
import aphyt.cip as ap
import binascii


def cip_crc16(data: bytes, poly=0xa001) -> bytes:
    data = bytearray(data)
    crc = 0x0000
    for byte in data:
        crc = crc ^ byte
        for _ in range(0, 8):
            carry = crc & 1
            crc >>= 1
            if carry:
                crc = crc ^ poly
    return crc.to_bytes(2, 'little')


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

    @property
    def bytes(self) -> bytes:
        return \
            self.request_service + self.request_path_size.to_bytes(1, 'little') + \
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

    @property
    def bytes(self) -> bytes:
        """
        The bytes in the CIP reply
        :return:
        """
        return \
            self.reply_service + self.reserved + self.general_status + \
            self.extended_status_size + self.extended_status + self.reply_data


class CIPCommonFormat:
    """
    CIP common format is a format that is used to pack data to be used in CIP messages
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

    def __repr__(self):
        return str(self.data_type + self.additional_info_length.to_bytes(1, 'little') + self.additional_info + self.data)

    def from_bytes(self, bytes_cip_common_format):
        self.data_type = bytes_cip_common_format[0:1]
        self.additional_info_length = int.from_bytes(bytes_cip_common_format[1:2], 'little')
        self.additional_info = bytes_cip_common_format[2:2 + self.additional_info_length]
        self.data = bytes_cip_common_format[2 + self.additional_info_length:]


class CIPDispatcher(ABC):
    """
    CIPDispatcher is an abstract base class that has the basic methods and data required
    to send and receive CIP messages from a peer that is equipped to communicate using
    this protocol

    The key method that subclasses need to implement is 'execute_cip_command' which will
    send a CIPRequest over the CIP network and receive a CIPReply

    ToDo monitor when the read, write, get, set services have all moved to CIP objects mixins and get rid of them
    """

    def __init__(self):
        self.variables = {}
        self.user_variables = {}
        self.system_variables = {}
        self.data_type_dictionary = {}

    @abstractmethod
    def execute_cip_command(self, request: CIPRequest) -> CIPReply:
        pass

    def read_tag_service(self, tag_request_path, number_of_elements=1) -> CIPReply:
        read_tag_request = \
            CIPRequest(ap.CIPService.READ_TAG_SERVICE, tag_request_path, number_of_elements.to_bytes(2, 'little'))
        return self.execute_cip_command(read_tag_request)

    def write_tag_service(self, tag_request_path, request_service_data: CIPCommonFormat, number_of_elements=1):
        data = request_service_data.data_type + \
               int(request_service_data.additional_info_length).to_bytes(1, 'little') + \
               request_service_data.additional_info + number_of_elements.to_bytes(2, 'little') + \
               request_service_data.data
        write_tag_request = CIPRequest(ap.CIPService.WRITE_TAG_SERVICE, tag_request_path, data)
        return self.execute_cip_command(write_tag_request)

    def read_tag_fragmented_service(self, tag_request_path, offset, number_of_elements):
        data = tag_request_path + number_of_elements.to_bytes(2, 'little') + offset.to_bytes(4, 'little')
        read_tag_fragmented_request = \
            CIPRequest(ap.CIPService.READ_TAG_FRAGMENTED_SERVICE, tag_request_path, data)
        return self.execute_cip_command(read_tag_fragmented_request)

    def write_tag_fragmented_service(self, tag_request_path, cip_datatype_code, data, offset, number_of_elements=1):
        data = \
            cip_datatype_code + b'\x00' + number_of_elements.to_bytes(2, 'little') + \
            offset.to_bytes(4, 'little') + data
        write_tag_fragmented_request = CIPRequest(ap.CIPService.WRITE_TAG_FRAGMENTED_SERVICE, tag_request_path, data)
        return self.execute_cip_command(write_tag_fragmented_request)

    def get_attribute_all_service(self, tag_request_path):
        get_attribute_all_request = CIPRequest(ap.CIPService.GET_ATTRIBUTE_ALL, tag_request_path)
        return self.execute_cip_command(get_attribute_all_request)

    def get_attribute_single_service(self, tag_request_path):
        get_attribute_single_request = CIPRequest(ap.CIPService.GET_ATTRIBUTE_SINGLE, tag_request_path)
        return self.execute_cip_command(get_attribute_single_request)

    def set_attribute_single_service(self, tag_request_path):
        set_attribute_single_request = CIPRequest(ap.CIPService.SET_ATTRIBUTE_SINGLE, tag_request_path)
        return self.execute_cip_command(set_attribute_single_request)


def address_request_path_segment(class_id: bytes = None, instance_id: bytes = None,
                                 attribute_id: bytes = None, element_id: bytes = None) -> bytes:
    """
    This function is to create a request path using the class, instance, attribute and element values
    of the data that the programmer will access

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
    This function is to create a request path using the variable name of the data that the programmer will access

    :param variable_name: The name of the variable for the request path
    :return: Request path as a bytes object
    """
    # Symbolic segment
    # 1756-pm020_-en-p.pdf 17 of 94
    request_path_bytes = b'\x91' + len(variable_name).to_bytes(1, 'little') + variable_name.encode('utf-8')
    if len(request_path_bytes) % 2 != 0:
        request_path_bytes = request_path_bytes + b'\x00'
    return request_path_bytes
