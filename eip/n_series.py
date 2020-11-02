__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from eip import *
from .cip_datatypes import _update_data_type_dictionary
from .omron_datatypes import *


class VariableTypeObjectReply(CIPReply):
    """
    CIP Reply from the Get Attribute All service to Variable Type Object Class Code 0x6C adding descriptive properties
    Omron Vendor specific
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
            dimension_size = struct.unpack("<L", self.reply_data[8 + i * 4:8 + i * 4 + 4])[0]
            dimension_size_list.append(dimension_size)
        return dimension_size_list

    @property
    def number_of_members(self):
        return struct.unpack("<H", self.reply_data[8 + self.array_dimension * 4:10 + self.array_dimension * 4])[0]

    @property
    def crc_code(self):
        return struct.unpack("<H", self.reply_data[14 + self.array_dimension * 4:16 + self.array_dimension * 4])[0]

    @property
    def variable_type_name_length(self):
        return struct.unpack("<B", self.reply_data[16 + self.array_dimension * 4:17 + self.array_dimension * 4])[0]

    @property
    def padding(self):
        if self.variable_type_name_length % 2 == 0:
            return 1
        else:
            return 0

    @property
    def variable_type_name(self):
        return \
            self.reply_data[17 + self.array_dimension * 4:
                            17 + self.array_dimension * 4 + self.variable_type_name_length]

    @property
    def next_instance_id(self):
        return \
            self.reply_data[self.padding + 17 + self.array_dimension * 4 + self.variable_type_name_length:
                            self.padding + 17 + self.array_dimension * 4 + self.variable_type_name_length + 4]

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
    Omron Vendor specific
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
            dimension_size = struct.unpack("<L", self.reply_data[8 + i * 4:8 + i * 4 + 4])[0]
            dimension_size_list.append(dimension_size)
        return dimension_size_list

    @property
    def bit_number(self):
        return struct.unpack("<B", self.reply_data[16 + self.array_dimension * 4:17 + self.array_dimension * 4])[0]

    @property
    def variable_type_instance_id(self):
        return self.reply_data[20 + self.array_dimension * 4:24 + self.array_dimension * 4]

    @property
    def start_array_elements(self):
        """Number of elements in each dimension of  the array"""
        array_start_list = []
        for i in range(self.array_dimension):
            array_start = \
                struct.unpack("<L",
                              self.reply_data[24 + self.array_dimension * 4:
                                              24 + self.array_dimension * 4 + 4])[0]
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

    def get_instance_list_service(self, tag_request_path: bytes, data: bytes):
        """Omron specific CIP service
        :param tag_request_path:
        :param data:
        :return:
        """
        get_instance_list_request = CIPRequest(b'\x5f', tag_request_path, data)
        return self.execute_cip_command(get_instance_list_request)

    def update_variable_dictionary(self):
        """
        Make sure the variable dictionary is populated with the
        latest variable and datatype information from controller
        :return:
        """
        _update_data_type_dictionary(self.data_type_dictionary)
        variable_list = self._get_variable_list()
        instance_id = 1
        for variable in variable_list:
            reply = self._get_variable_object(instance_id)
            variable_cip_datatype = self.data_type_dictionary.get(reply.cip_data_type)()
            if not isinstance(variable_cip_datatype, type(None)):
                variable_cip_datatype.instance_id = instance_id
                # Instantiate the classes into objects
                variable_cip_datatype = self._get_data_instance(variable_cip_datatype)
                variable_cip_datatype.variable_name = variable
                self.variables.update({variable: variable_cip_datatype})
                if variable[0:1] == '_':
                    self.system_variables.update({variable: variable_cip_datatype})
                else:
                    self.user_variables.update({variable: variable_cip_datatype})
            instance_id = instance_id + 1

    def _get_data_instance(self, cip_datatype_instance: CIPDataType) -> CIPDataType:
        # ToDo TESTS
        if isinstance(cip_datatype_instance, CIPArray):
            variable_object_reply = self._get_variable_object(cip_datatype_instance.instance_id)
            if variable_object_reply.variable_type_instance_id == b'\x00\x00\x00\x00':
                cip_datatype_instance.from_items(variable_object_reply.cip_data_type_of_array,
                                                 variable_object_reply.size,
                                                 variable_object_reply.array_dimension,
                                                 variable_object_reply.number_of_elements,
                                                 variable_object_reply.start_array_elements)
            else:
                member_instance_id = int.from_bytes(variable_object_reply.variable_type_instance_id, 'little')
                member_instance = self._get_member_instance(member_instance_id)
                cip_datatype_instance.from_instance(member_instance,
                                                    variable_object_reply.size,
                                                    variable_object_reply.array_dimension,
                                                    variable_object_reply.number_of_elements,
                                                    variable_object_reply.start_array_elements)
            return cip_datatype_instance

        elif isinstance(cip_datatype_instance, CIPString):
            variable_object_reply = self._get_variable_object(cip_datatype_instance.instance_id)
            cip_datatype_instance.size = variable_object_reply.size
            return cip_datatype_instance

        elif isinstance(cip_datatype_instance, CIPAbbreviatedStructure):
            pass

        elif isinstance(cip_datatype_instance, CIPStructure):
            variable_object_reply = self._get_variable_object(cip_datatype_instance.instance_id)
            variable_type_instance_id = int.from_bytes(variable_object_reply.variable_type_instance_id, 'little')
            variable_type_object_reply = self._get_variable_type_object(variable_type_instance_id)
            cip_datatype_instance.variable_type_name = variable_type_object_reply.variable_type_name
            cip_datatype_instance.size = variable_type_object_reply.size_in_memory
            nesting_variable_type_instance_id = \
                int.from_bytes(variable_type_object_reply.nesting_variable_type_instance_id, 'little')
            member_instance_id = nesting_variable_type_instance_id
            while member_instance_id != 0:
                member_cip_datatype_instance = self._get_member_instance(member_instance_id)
                cip_datatype_instance.members.update(
                    {member_cip_datatype_instance.variable_name: member_cip_datatype_instance})
                member_instance_id = \
                    int.from_bytes(member_cip_datatype_instance.next_instance_id, 'little')
            return cip_datatype_instance
        else:
            cip_datatype_instance = self.data_type_dictionary.get(cip_datatype_instance.data_type_code())()
            return cip_datatype_instance

    def _get_member_instance(self, member_instance_id: int) -> CIPDataType:
        variable_type_object_reply = self._get_variable_type_object(member_instance_id)
        cip_datatype_instance = self.data_type_dictionary.get(variable_type_object_reply.cip_data_type)()
        cip_datatype_instance.variable_name = variable_type_object_reply.variable_type_name
        cip_datatype_instance.size = variable_type_object_reply.size_in_memory
        cip_datatype_instance.next_instance_id = variable_type_object_reply.next_instance_id
        cip_datatype_instance.nesting_variable_type_instance_id = \
            variable_type_object_reply.nesting_variable_type_instance_id
        if isinstance(cip_datatype_instance, CIPArray):
            array_start_list = []
            for i in range(variable_type_object_reply.array_dimension):
                array_start = 0
                array_start_list.append(array_start)
            cip_datatype_instance.from_items(variable_type_object_reply.cip_data_type_of_array,
                                             variable_type_object_reply.size_in_memory,
                                             variable_type_object_reply.array_dimension,
                                             variable_type_object_reply.number_of_elements,
                                             array_start_list)
            return cip_datatype_instance

        elif isinstance(cip_datatype_instance, CIPString):
            cip_datatype_instance.size = variable_type_object_reply.size_in_memory
            return cip_datatype_instance

        elif isinstance(cip_datatype_instance, CIPAbbreviatedStructure):
            pass

        elif isinstance(cip_datatype_instance, CIPStructure):
            member_instance_id = int.from_bytes(cip_datatype_instance.nesting_variable_type_instance_id, 'little')
            while member_instance_id != 0:
                variable_type_object_reply = self._get_variable_type_object(member_instance_id)
                member_cip_datatype_instance = self._get_member_instance(member_instance_id)
                # The memory alignment of a structure is the same as the largest aligned member
                if member_cip_datatype_instance.alignment > cip_datatype_instance.alignment:
                    cip_datatype_instance.alignment = member_cip_datatype_instance.alignment
                cip_datatype_instance.members.update(
                    {variable_type_object_reply.variable_type_name: member_cip_datatype_instance})
                member_instance_id = \
                    int.from_bytes(variable_type_object_reply.next_instance_id, 'little')
            return cip_datatype_instance
        else:
            # cip_datatype_instance = self.data_type_dictionary.get(cip_datatype_instance.data_type_code())()
            return cip_datatype_instance

    def read_variable(self, variable_name: str):
        request_path = variable_request_path_segment(variable_name)
        cip_datatype_object = self.variables.get(variable_name)
        if isinstance(cip_datatype_object, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            return self._multi_message_variable_read(cip_datatype_object)
        else:
            response = self.read_tag_service(request_path)
            cip_datatype_object.from_bytes(response.reply_data)
            return cip_datatype_object.value()

    def write_variable(self, variable_name: str, data):
        request_path = variable_request_path_segment(variable_name)
        cip_datatype_object = self.variables.get(variable_name)
        cip_datatype_object.from_value(data)
        if isinstance(cip_datatype_object, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            self._multi_message_variable_write(cip_datatype_object, data)
        else:
            request_data = CIPCommonFormat(cip_datatype_object.data_type_code(), data=cip_datatype_object.data)
            self.write_tag_service(request_path, request_data)

    def _multi_message_variable_read(self, cip_datatype_object: CIPDataType, offset=0):
        max_read_size = self.MAXIMUM_LENGTH - 8
        data = b''
        while offset < cip_datatype_object.size:
            if cip_datatype_object.size - offset > max_read_size:
                read_size = max_read_size
            else:
                read_size = cip_datatype_object.size - offset
            response = self._simple_data_segment_read(cip_datatype_object, offset, read_size)
            reply_bytes = response.reply_data
            cip_common_format = CIPCommonFormat()
            cip_common_format.from_bytes(reply_bytes)
            if isinstance(cip_datatype_object, CIPString):
                # First two characters of the string seem to be how many characters were read
                data = data + cip_common_format.data[2:]
            elif isinstance(cip_datatype_object, CIPStructure):
                cip_datatype_object.crc_code = cip_common_format.additional_info
                data = data + cip_common_format.data
            else:
                data = data + cip_common_format.data
            offset = offset + max_read_size
        cip_datatype_object.data = data
        cip_datatype_object.size = len(data)
        return cip_datatype_object.value()

    def _multi_message_variable_write(self, cip_datatype_object: CIPDataType, data, offset=0):
        max_write_size = 400
        cip_datatype_object.from_value(data)
        write_size = max_write_size
        while offset < cip_datatype_object.size:
            if cip_datatype_object.size - offset > max_write_size:
                write_size = max_write_size
            else:
                write_size = cip_datatype_object.size - offset
            response = self._simple_data_segment_write(
                cip_datatype_object, offset, write_size,
                cip_datatype_object.data[offset:offset + write_size])
            offset = offset + max_write_size

    def _simple_data_segment_read(self, cip_datatype_object: CIPDataType, offset, read_size):
        # ToDo consider the request path should reside with the variable (possibly converted to logical segment)
        request_path = variable_request_path_segment(cip_datatype_object.variable_name)
        simple_data_request_path = SimpleDataSegmentRequest(offset, read_size)
        request_path = request_path + simple_data_request_path.bytes()
        response = self.read_tag_service(request_path)
        return response

    def _simple_data_segment_write(self, cip_datatype_object: CIPDataType, offset, write_size, data):
        request_path = variable_request_path_segment(cip_datatype_object.variable_name)
        simple_data_request_path = SimpleDataSegmentRequest(offset, write_size)
        request_path = request_path + simple_data_request_path.bytes()
        # ToDo how to prevent testing type code here. Function is doing too much
        response = None
        if cip_datatype_object.data_type_code() == CIPString.data_type_code():
            data = struct.pack("<H", len(data)) + data
            request_data = CIPCommonFormat(cip_datatype_object.data_type_code(), data=data)
            response = self.write_tag_service(request_path, request_data)
        elif cip_datatype_object.data_type_code() == CIPArray.data_type_code():
            request_data = CIPCommonFormat(cip_datatype_object.array_data_type, data=data)
            response = self.write_tag_service(request_path, request_data)
        elif cip_datatype_object.data_type_code() == CIPStructure.data_type_code():
            request_data = CIPCommonFormat(CIPAbbreviatedStructure.data_type_code(), additional_info_length=2,
                                           additional_info=cip_datatype_object.crc_code, data=data)
            response = self.write_tag_service(request_path, request_data)
        return response

    def _cip_string_read(self, request_path):
        pass

    def _cip_string_write(self):
        pass

    def _cip_structure_read(self):
        pass

    def _cip_structure_write(self):
        pass

    def _cip_abbreviated_structure_read(self):
        pass

    def _cip_abbreviated_structure_write(self):
        pass

    def _cip_array_read(self):
        pass

    def _cip_array_write(self):
        pass

    def _get_variable_type_object(self, instance_id: int) -> VariableTypeObjectReply:
        request_path = address_request_path_segment(
            class_id=b'\x6c', instance_id=instance_id.to_bytes(2, 'little'))
        variable_type_object_reply = VariableTypeObjectReply(self.get_attribute_all_service(request_path).bytes)
        return variable_type_object_reply

    def _get_variable_object(self, instance_id: int) -> VariableObjectReply:
        request_path = address_request_path_segment(
            class_id=b'\x6b', instance_id=instance_id.to_bytes(2, 'little'))
        variable_object_reply = VariableObjectReply(self.get_attribute_all_service(request_path).bytes)
        return variable_object_reply

    def _get_variable_list(self):
        """

        :return:
        """
        tag_list = []
        for tag_index in range(self._get_number_of_variables()):
            offset = tag_index + 1
            request_path = address_request_path_segment(b'\x6a', offset.to_bytes(2, 'little'))
            reply = self.get_attribute_all_service(request_path)
            tag = str(reply.reply_data[5:5 + int.from_bytes(reply.reply_data[4:5], 'little')], 'utf-8')
            tag_list.append(tag)
        return tag_list

    def _get_number_of_variables(self) -> int:
        """
        Find number of variables from Tag Name Server
        :return:
        """
        request_path = address_request_path_segment(b'\x6a', b'\x00\x00')
        reply = self.get_attribute_all_service(request_path)
        return int.from_bytes(reply.reply_data[2:4], 'little')
