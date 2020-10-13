__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from eip import *
from .omron_datatypes import *


class VariableTypeObjectReply(CIPReply):
    """
    CIP Reply from the Get Attribute All service to Variable Type Object Class Code 0x6C adding descriptive properties
    """
    def __init__(self, reply_bytes: bytes):
        super().__init__(reply_bytes=reply_bytes)

    @property
    def size_in_memory(self):
        return struct.unpack("<L", self.reply_data[0:4])[0]

    @property
    def cip_data_type(self):
        return self.reply_data[5:6]

    @property
    def cip_data_type_of_array(self):
        return self.reply_data[6:7]

    @property
    def array_dimension(self):
        return struct.unpack("<B", self.reply_data[7:8])[0]

    @property
    def number_of_elements(self):
        """Number of elements in each dimension of  the array"""
        dimension_size_list = []
        for i in range(self.array_dimension):
            dimension_size = struct.unpack("<L", self.reply_data[8+i*4:8+i*4+4])[0]
            dimension_size_list.append(dimension_size)
        return dimension_size_list

    @property
    def number_of_members(self):
        return struct.unpack("<H", self.reply_data[8+self.array_dimension*4:10+self.array_dimension*4])[0]

    @property
    def crc_code(self):
        return struct.unpack("<H", self.reply_data[14+self.array_dimension*4:16+self.array_dimension*4])[0]

    @property
    def variable_type_name_length(self):
        return struct.unpack("<B", self.reply_data[16+self.array_dimension*4:17+self.array_dimension*4])[0]

    @property
    def padding(self):
        if self.variable_type_name_length % 2 == 0:
            return 1
        else:
            return 0

    @property
    def variable_type_name(self):
        return \
            self.reply_data[17+self.array_dimension*4:
                            17+self.array_dimension*4+self.variable_type_name_length]

    @property
    def next_instance_id(self):
        return \
            self.reply_data[self.padding+17+self.array_dimension*4+self.variable_type_name_length:
                            self.padding+17+self.array_dimension*4+self.variable_type_name_length+4]

    @property
    def nesting_variable_type_instance_id(self):
        return \
            self.reply_data[self.padding + 21 + self.array_dimension * 4 + self.variable_type_name_length:
                            self.padding + 21 + self.array_dimension * 4 + self.variable_type_name_length + 4]

    @property
    def start_array_elements(self):
        """Number of elements in each dimension of  the array"""
        array_start_list = []
        for i in range(self.array_dimension):
            array_start = \
                struct.unpack("<L",
                              self.reply_data[self.padding + 25 +
                                              self.array_dimension * 4 +
                                              self.variable_type_name_length:
                                              self.padding + 25 +
                                              self.array_dimension * 4 +
                                              self.variable_type_name_length + 4])[0]
            array_start_list.append(array_start)
        return array_start_list


class VariableObjectReply(CIPReply):
    """
    CIP Reply from the Get Attribute All service to Variable Object Class Code 0x6B adding descriptive properties
    """
    def __init__(self, reply_bytes: bytes):
        super().__init__(reply_bytes=reply_bytes)

    @property
    def size(self):
        return struct.unpack("<L", self.reply_data[0:4])[0]

    @property
    def cip_data_type(self):
        return self.reply_data[4:5]

    @property
    def cip_data_type_of_array(self):
        return self.reply_data[5:6]

    @property
    def array_dimension(self):
        # One byte of padding after this. Skip to byte 8
        return struct.unpack("<B", self.reply_data[6:7])[0]

    @property
    def number_of_elements(self):
        """Number of elements in each dimension of  the array"""
        dimension_size_list = []
        for i in range(self.array_dimension):
            dimension_size = struct.unpack("<L", self.reply_data[8+i*4:8+i*4+4])[0]
            dimension_size_list.append(dimension_size)
        return dimension_size_list

    @property
    def bit_number(self):
        return struct.unpack("<B", self.reply_data[16+self.array_dimension*4:17+self.array_dimension*4])[0]

    @property
    def variable_type_instance_id(self):
        return self.reply_data[20+self.array_dimension*4:24+self.array_dimension*4]

    @property
    def start_array_elements(self):
        """Number of elements in each dimension of  the array"""
        array_start_list = []
        for i in range(self.array_dimension):
            array_start = \
                struct.unpack("<L",
                              self.reply_data[24+self.array_dimension * 4:
                                              24+self.array_dimension * 4 + 4])[0]
            array_start_list.append(array_start)
        return array_start_list


class SimpleDataSegmentRequest:
    def __init__(self, offset, size):
        self.simple_data_type_code = b'\x80'
        self.segment_length = b'\x03'  # Fixed and in words
        self.offset = offset
        self.size = size

    def bytes(self):
        return \
            self.simple_data_type_code + self.segment_length + \
            struct.pack("<L", self.offset) + struct.pack("<H", self.size)


class NSeriesEIP(EIP):
    MAXIMUM_LENGTH = 502  # UCMM maximum length is 502 bytes

    def __init__(self):
        super().__init__()

    def get_attribute_all_service(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_all_request = CIPRequest(CIPService.GET_ATTRIBUTE_ALL, tag_route_path)
        return self.execute_cip_command(get_attribute_all_request)

    def get_attribute_single_service(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_single_request = CIPRequest(CIPService.GET_ATTRIBUTE_SINGLE, tag_route_path)
        return self.execute_cip_command(get_attribute_single_request)

    def get_instance_list_service(self, tag_route_path, data):
        get_instance_list_request = CIPRequest(b'\x5f', tag_route_path, data)
        return self.execute_cip_command(get_instance_list_request)

    def read_variable(self, variable_name: str):
        route_path = variable_request_path_segment(variable_name)
        cip_datatype = self.variables.get(variable_name)
        if isinstance(cip_datatype, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            return self._multi_message_variable_read(variable_name)
        else:
            response = self.read_tag_service(route_path)
            cip_datatype.from_bytes(response.reply_data)
            return cip_datatype.value()

    def _simple_data_segment_read(self, variable_name, offset, read_size):
        route_path = variable_request_path_segment(variable_name)
        simple_data_route_path = SimpleDataSegmentRequest(offset, read_size)
        route_path = route_path + simple_data_route_path.bytes()
        response = self.read_tag_service(route_path)
        return response

    def _simple_data_segment_write(self, variable_name, offset, write_size, data_type_code, data):
        route_path = variable_request_path_segment(variable_name)
        simple_data_route_path = SimpleDataSegmentRequest(offset, write_size)
        route_path = route_path + simple_data_route_path.bytes()
        data = struct.pack("<H", len(data)) + data
        response = self.write_tag_service(
            route_path, data_type_code, data)
        return response

    def _multi_message_variable_read(self, variable_name, offset=0):
        max_read_size = self.MAXIMUM_LENGTH - 8
        cip_datatype = self.variables.get(variable_name)
        data = b''
        while offset < cip_datatype.size:
            if cip_datatype.size - offset > max_read_size:
                read_size = max_read_size
            else:
                read_size = cip_datatype.size - offset
            response = self._simple_data_segment_read(variable_name, offset, read_size)
            data = data + response.reply_data[4:]
            offset = offset + max_read_size
        cip_datatype.data = data
        return cip_datatype.value()

    def write_variable(self, variable_name: str, data):
        route_path = variable_request_path_segment(variable_name)
        cip_datatype = self.variables.get(variable_name)
        cip_datatype.from_value(data)
        if isinstance(cip_datatype, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            self._multi_message_variable_write(variable_name, data)
        else:
            self.write_tag_service(route_path, cip_datatype.data_type_code(), cip_datatype.data)

    def _multi_message_variable_write(self, variable_name, data, offset=0):
        message_overhead = 8
        if message_overhead % 2 == 1:
            message_overhead = message_overhead + 1
        max_write_size = self.MAXIMUM_LENGTH - message_overhead
        cip_datatype = self.variables.get(variable_name)
        cip_datatype.from_value(data)
        while offset < cip_datatype.size:
            if cip_datatype.size - offset > max_write_size:
                write_size = max_write_size
            else:
                write_size = cip_datatype.size - offset
            response = self._simple_data_segment_write(
                variable_name, offset, write_size,
                cip_datatype.data_type_code(), cip_datatype.data[offset:offset + write_size])
            offset = offset + max_write_size

    def update_variable_dictionary(self):
        """

        :return:
        """
        self._update_data_type_dictionary()
        variable_list = self._get_variable_list()
        instance_id = 1
        for variable in variable_list:

            route_path = eip.address_request_path_segment(
                class_id=b'\x6b', instance_id=instance_id.to_bytes(2, 'little'))
            reply = VariableObjectReply(self.get_attribute_all_service(route_path).bytes)
            variable_cip_datatype = self.data_type_dictionary.get(reply.cip_data_type)
            if not isinstance(variable_cip_datatype, type(None)):
                # Instantiate the classes into objects
                if reply.array_dimension != 0:
                    variable_cip_datatype = \
                        variable_cip_datatype(reply.cip_data_type_of_array,
                                              reply.size,
                                              reply.array_dimension,
                                              reply.number_of_elements,
                                              reply.start_array_elements)
                else:
                    variable_cip_datatype = variable_cip_datatype()
                    variable_cip_datatype.size = reply.size
                variable_cip_datatype.attribute_id = instance_id
                self.variables.update({variable: variable_cip_datatype})
                if variable[0:1] == '_':
                    self.system_variables.update({variable: variable_cip_datatype})
                else:
                    self.user_variables.update({variable: variable_cip_datatype})
            instance_id = instance_id + 1

    def _update_data_type_dictionary(self):
        for sub_class in CIPDataType.__subclasses__():
            self.data_type_dictionary.update({sub_class.data_type_code(): sub_class})

    def _get_variable_list(self):
        """

        :return:
        """
        tag_list = []
        for tag_index in range(self._get_number_of_variables()):
            offset = tag_index + 1
            route_path = address_request_path_segment(b'\x6a', offset.to_bytes(2, 'little'))
            reply = self.get_attribute_all_service(route_path)
            tag = str(reply.reply_data[5:5 + int.from_bytes(reply.reply_data[4:5], 'little')], 'utf-8')
            tag_list.append(tag)
        return tag_list

    def _get_number_of_variables(self) -> int:
        """
        Find number of variables from Tag Name Server
        :return:
        """
        route_path = address_request_path_segment(b'\x6a', b'\x00\x00')
        reply = self.get_attribute_all_service(route_path)
        return int.from_bytes(reply.reply_data[2:4], 'little')
