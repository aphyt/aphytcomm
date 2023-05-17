__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import concurrent.futures
import pickle
import socket
import struct
import sys
import threading
from signal import signal, SIGINT

from aphyt.eip import *
import logging


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
    def size(self):
        return self.size_in_memory

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
    """
    A simple data segment request is the Omron specific format for requesting data that will not fit
    in a single CIP message. This is used for strings, arrays and structures
    """

    def __init__(self, offset, size):
        self.simple_data_type_code = b'\x80'
        self.segment_length = b'\x03'  # Fixed and in words
        self.offset = offset
        self.size = size

    def bytes(self):
        return \
            self.simple_data_type_code + self.segment_length + \
            struct.pack("<L", self.offset) + struct.pack("<H", self.size)


class NSeries:
    """
    NSeries
    ~~~~~~~

    Class that implements Omron N-Series specific Ethernet/IP services in addition to Ethernet/IP services
    and CIP services common to most Ethernet/IP devices
    """
    MAXIMUM_LENGTH = 502  # UCMM maximum length is 502 bytes

    def __init__(self):
        super().__init__()
        self.derived_data_type_dictionary = {}
        self.connected_cip_dispatcher = EIPConnectedCIPDispatcher()

    def connect_explicit(self, host):
        self.connected_cip_dispatcher.connect_explicit(host)

    def close_explicit(self):
        self.connected_cip_dispatcher.close_explicit()

    def register_session(self):
        self.connected_cip_dispatcher.register_session()

    def get_instance_list_service(self, tag_request_path: bytes, data: bytes):
        """
        Omron specific CIP service
        :param tag_request_path:
        :param data:
        :return:
        """
        get_instance_list_request = CIPRequest(b'\x5f', tag_request_path, data)
        return self.connected_cip_dispatcher.execute_cip_command(get_instance_list_request)

    def update_derived_data_type_dictionary(self, display=False):
        # ToDo get the derived data types in such  a way they are easy to use
        number_of_entries = self._get_number_of_derived_data_types()
        for index in range(1, number_of_entries + 1):
            reply = self._get_variable_type_object(index)
            if display:
                print('index: %s '
                      'size: %s '
                      'type: %s '
                      'array type: %s '
                      'dimensions: %s '
                      'elements: %s '
                      'number of members: %s '
                      'crc: %s '
                      'variable name length: %s '
                      'variable type name: %s '
                      'next instance id: %s '
                      'nesting variable type instance id %s '
                      'start array elements %s' %
                      (str(index),
                       str(reply.size_in_memory),
                       str(reply.cip_data_type),
                       str(reply.cip_data_type_of_array),
                       str(reply.array_dimension),
                       str(reply.number_of_elements),
                       str(reply.number_of_members),
                       str(reply.crc_code),
                       str(reply.variable_type_name_length),
                       str(reply.variable_type_name),
                       str(reply.next_instance_id),
                       str(reply.nesting_variable_type_instance_id),
                       str(reply.start_array_elements)
                       ))

    def update_variable_dictionary(self):
        """
        Make sure the variable dictionary is populated with the
        latest variable and datatype information from controller
        :return:
        """
        update_data_type_dictionary(self.connected_cip_dispatcher.data_type_dictionary)
        variable_list = self._get_variable_list()
        instance_id = 1
        for variable in variable_list:
            # Instantiate the classes into objects
            variable_cip_datatype = self._get_instance_from_variable_object_id(instance_id)
            variable_cip_datatype.variable_name = str(variable)
            self.connected_cip_dispatcher.variables.update({variable: variable_cip_datatype})
            if variable[0:1] == '_':
                self.connected_cip_dispatcher.system_variables.update({variable: variable_cip_datatype})
            else:
                self.connected_cip_dispatcher.user_variables.update({variable: variable_cip_datatype})
            instance_id = instance_id + 1

    def save_current_dictionary(self, file_name: str):
        with (open(file_name, "wb")) as f:
            pickle.dump(self.connected_cip_dispatcher.variables, f)

    def load_dictionary_file(self, file_name: str):
        with (open(file_name, "rb")) as f:
            self.connected_cip_dispatcher.variables = pickle.load(f)

    def load_dictionary_file_if_present(self, file_name: str):
        """
        If the supplied file name exists, load it as the controller's dictionary, and if not, pull it
        from the controller and save the dictionary as the supplied file name.

        This allows the programmer to use a file instead of network operation to quickly populate the variable
        dictionary, and if the controller's variable dictionary changes, the user can get the new values
        by simply deleting the file and it will be repopulated on the next run.
        :param file_name:
        :return:
        """
        try:
            with (open(file_name, "rb")) as f:
                self.connected_cip_dispatcher.variables = pickle.load(f)
        except IOError as err:
            self.update_variable_dictionary()
            self.save_current_dictionary(file_name)

    def _structure_instance_from_variable_object(
            self, variable_object: (VariableObjectReply, VariableTypeObjectReply)) -> CIPStructure:
        cip_datatype_instance = CIPStructure()
        variable_type_object_reply = None
        if isinstance(variable_object, VariableObjectReply):
            variable_type_instance_id = int.from_bytes(variable_object.variable_type_instance_id, 'little')
            variable_type_object_reply = self._get_variable_type_object(variable_type_instance_id)
            cip_datatype_instance.variable_type_name = str(variable_type_object_reply.variable_type_name, 'utf-8')
            cip_datatype_instance.size = variable_object.size
        if isinstance(variable_object, VariableTypeObjectReply):
            variable_type_instance_id = int.from_bytes(variable_object.nesting_variable_type_instance_id, 'little')
            variable_type_object_reply = self._get_variable_type_object(variable_type_instance_id)
            cip_datatype_instance.size = variable_type_object_reply.size_in_memory
            cip_datatype_instance.variable_type_name = str(variable_type_object_reply.variable_type_name, 'utf-8')

        nesting_variable_type_instance_id = \
            int.from_bytes(variable_type_object_reply.nesting_variable_type_instance_id, 'little')
        member_instance_id = nesting_variable_type_instance_id
        while member_instance_id != 0:
            variable_type_object_reply = self._get_variable_type_object(member_instance_id)
            member_cip_datatype_instance = self._get_member_instance(member_instance_id)
            if type(member_cip_datatype_instance) == CIPStructure:
                member_cip_datatype_instance.callback = cip_datatype_instance.from_value
                member_cip_datatype_instance.callback_arg = cip_datatype_instance
            member_name = str(variable_type_object_reply.variable_type_name, 'utf-8')
            cip_datatype_instance.members.update(
                {member_name: member_cip_datatype_instance})
            member_instance_id = \
                int.from_bytes(variable_type_object_reply.next_instance_id, 'little')
        return cip_datatype_instance

    def _array_instance_from_variable_object(
            self, variable_object: (VariableObjectReply, VariableTypeObjectReply)) -> CIPArray:
        cip_array_instance = CIPArray()
        variable_type_instance_id = b'\x00\x00\x00\x00'
        if isinstance(variable_object, VariableObjectReply):
            variable_type_instance_id = variable_object.variable_type_instance_id
        if variable_type_instance_id == b'\x00\x00\x00\x00':
            cip_array_instance.from_items(variable_object.cip_data_type_of_array,
                                          variable_object.size,
                                          variable_object.array_dimension,
                                          variable_object.number_of_elements,
                                          variable_object.start_array_elements)
        else:
            member_instance_id = int.from_bytes(variable_object.variable_type_instance_id, 'little')
            member_instance = self._get_member_instance(member_instance_id)
            cip_array_instance = member_instance
        return cip_array_instance

    @staticmethod
    def _string_instance_from_variable_object(
            variable_object: (VariableObjectReply, VariableTypeObjectReply)) -> CIPString:
        cip_string = CIPString()
        cip_string.size = variable_object.size
        return cip_string

    def _get_instance_from_variable_object_id(self, instance_id: int) -> CIPDataType:
        reply = self._get_variable_object(instance_id)
        if reply.cip_data_type == CIPStructure.data_type_code():
            return self._structure_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPAbbreviatedStructure.data_type_code():
            return self._structure_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPString.data_type_code():
            return self._string_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPArray.data_type_code():
            return self._array_instance_from_variable_object(reply)
        else:
            return self.connected_cip_dispatcher.data_type_dictionary.get(reply.cip_data_type)()

    def _get_member_instance(self, member_instance_id: int) -> CIPDataType:
        """
        This method returns a CIP datatype instance from a member ID. This is how the driver can
        build instances of derived data types like structures and arrays of structures
        :param member_instance_id:
        :return:
        """
        reply = self._get_variable_type_object(member_instance_id)
        if reply.cip_data_type == CIPStructure.data_type_code():
            return self._structure_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPAbbreviatedStructure.data_type_code():
            return self._structure_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPString.data_type_code():
            return self._string_instance_from_variable_object(reply)
        elif reply.cip_data_type == CIPArray.data_type_code():
            return self._array_instance_from_variable_object(reply)
        else:
            return self.connected_cip_dispatcher.data_type_dictionary.get(reply.cip_data_type)()

    def read_variable(self, variable_name: str):
        """
        This method will read the variable name from the controller and return it in the corresponding
        Python datatype
        :param variable_name:
        :return:
        """
        request_path = variable_request_path_segment(variable_name)
        cip_datatype_object = self.connected_cip_dispatcher.variables.get(variable_name)
        if isinstance(cip_datatype_object, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            return self._multi_message_variable_read(cip_datatype_object)
        else:
            response = self.connected_cip_dispatcher.read_tag_service(request_path)
            cip_datatype_object.from_bytes(response.reply_data)
            return cip_datatype_object.value()

    def write_variable(self, variable_name: str, data):
        """
        This method takes a variable name and formats the Python datatype into the correct CIP datatype
        and writes it to the controller
        :param variable_name:
        :param data:
        :return:
        """
        request_path = variable_request_path_segment(variable_name)
        cip_datatype_object = self.connected_cip_dispatcher.variables.get(variable_name)
        cip_datatype_object.from_value(data)
        if isinstance(cip_datatype_object, (CIPString, CIPArray, CIPStructure, CIPAbbreviatedStructure)):
            self._multi_message_variable_write(cip_datatype_object, data)
        else:
            request_data = CIPCommonFormat(cip_datatype_object.data_type_code(), data=cip_datatype_object.data)
            self.connected_cip_dispatcher.write_tag_service(request_path, request_data)

    def verified_write_variable(self, variable_name: str, data, retry_count: int = 2):
        remaining_retry = retry_count
        temp_data = None
        while remaining_retry >= 0 and temp_data != data:
            self.write_variable(variable_name, data)
            temp_data = self.read_variable(variable_name)
            remaining_retry += -1
        if remaining_retry < 0 and temp_data != data:
            logging.warning('Write Operation could not be completed within specified retry count')
            raise IOError('Write Operation could not be completed within specified retry count')

    def _multi_message_variable_read(self, cip_datatype_object: CIPDataType, offset=0):
        """
        This method is to read data that does not fit into a single CIP message
        :param cip_datatype_object:
        :param offset:
        :return:
        """
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
        # cip_datatype_object.size = len(data) # Removed Why did it exist? If weird stuff breaks revisit
        return cip_datatype_object.value()

    def _multi_message_variable_write(self, cip_datatype_object: CIPDataType, data, offset=0):
        """
        This method is to write data that does not fit into a single CIP message
        :param cip_datatype_object:
        :param data:
        :param offset:
        :return:
        """
        max_write_size = 400
        cip_datatype_object.from_value(data)
        if isinstance(cip_datatype_object, CIPArray):
            max_write_size = max_write_size // cip_datatype_object.array_data_type_size * \
                             cip_datatype_object.array_data_type_size
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
        """
        This method formats as request path to be used with simple_data_segment reading operations
        :param cip_datatype_object:
        :param offset:
        :param read_size:
        :return:
        """
        # ToDo consider the request path should reside with the variable (possibly converted to logical segment)
        request_path = variable_request_path_segment(cip_datatype_object.variable_name)
        simple_data_request_path = SimpleDataSegmentRequest(offset, read_size)
        request_path = request_path + simple_data_request_path.bytes()
        response = self.connected_cip_dispatcher.read_tag_service(request_path)
        return response

    def _simple_data_segment_write(self, cip_datatype_object: CIPDataType, offset, write_size, data):
        """
        This method formats as request path to be used with simple_data_segment writing operations
        :param cip_datatype_object:
        :param offset:
        :param write_size:
        :param data:
        :return:
        """
        request_path = variable_request_path_segment(cip_datatype_object.variable_name)
        simple_data_request_path = SimpleDataSegmentRequest(offset, write_size)
        request_path = request_path + simple_data_request_path.bytes()
        # ToDo how to prevent testing type code here. Function is doing too much
        response = None
        if cip_datatype_object.data_type_code() == CIPString.data_type_code():
            data = struct.pack("<H", len(data)) + data
            request_data = CIPCommonFormat(cip_datatype_object.data_type_code(), data=data)
            response = self.connected_cip_dispatcher.write_tag_service(request_path, request_data)
        elif cip_datatype_object.data_type_code() == CIPArray.data_type_code():
            # ToDo Test String array. Probably have to put the length
            if cip_datatype_object.array_data_type == CIPStructure.data_type_code():
                array_variable_object = self._get_variable_object(cip_datatype_object.instance_id)
                structure_variable_type_object = \
                    self._get_variable_type_object(
                        int.from_bytes(array_variable_object.variable_type_instance_id, 'little'))
                crc_code = structure_variable_type_object.crc_code.to_bytes(2, 'little')
                request_data = CIPCommonFormat(CIPAbbreviatedStructure.data_type_code(), additional_info_length=2,
                                               additional_info=crc_code,
                                               data=data)
            else:
                request_data = CIPCommonFormat(cip_datatype_object.array_data_type, data=data)
            response = self.connected_cip_dispatcher.write_tag_service(request_path, request_data)
        elif cip_datatype_object.data_type_code() == CIPStructure.data_type_code():
            request_data = CIPCommonFormat(CIPAbbreviatedStructure.data_type_code(), additional_info_length=2,
                                           additional_info=cip_datatype_object.crc_code, data=data)
            response = self.connected_cip_dispatcher.write_tag_service(request_path, request_data)
        return response

    def _get_variable_type_object(self, instance_id: int) -> VariableTypeObjectReply:
        """
        Omron specific CIP class that is used to describe variable types. This is where derived data types
        will have their member definitions
        :param instance_id:
        :return:
        """
        request_path = address_request_path_segment(
            class_id=b'\x6c', instance_id=instance_id.to_bytes(2, 'little'))
        variable_type_object_reply = VariableTypeObjectReply(
            self.connected_cip_dispatcher.get_attribute_all_service(request_path).bytes)
        return variable_type_object_reply

    def _get_number_of_derived_data_types(self) -> int:
        request_path = eip.address_request_path_segment(class_id=b'\x6c', instance_id=int(0).to_bytes(2, 'little'))
        reply = self.connected_cip_dispatcher.get_attribute_all_service(request_path)
        max_instance = struct.unpack("<H", reply.reply_data[2:4])[0]
        return max_instance

    def _get_variable_object(self, instance_id: int) -> VariableObjectReply:
        """
        Omron specific CIP class that is used to describe variables. This contains critical information if the
        variable is an array type
        :param instance_id:
        :return:
        """
        request_path = address_request_path_segment(
            class_id=b'\x6b', instance_id=instance_id.to_bytes(2, 'little'))
        variable_object_reply = VariableObjectReply(
            self.connected_cip_dispatcher.get_attribute_all_service(request_path).bytes)
        return variable_object_reply

    def _get_variable_list(self):
        """
        Omron specific method for creating a list of variables that are published in the controller.
        :return:
        """
        tag_list = []
        for tag_index in range(self._get_number_of_variables()):
            offset = tag_index + 1
            request_path = address_request_path_segment(b'\x6a', offset.to_bytes(2, 'little'))
            reply = self.connected_cip_dispatcher.get_attribute_all_service(request_path)
            tag = str(reply.reply_data[5:5 + int.from_bytes(reply.reply_data[4:5], 'little')], 'utf-8')
            tag_list.append(tag)
        return tag_list

    def _get_number_of_variables(self) -> int:
        """
        Omron specific method to find number of variables from Tag Name Server
        :return:
        """
        request_path = address_request_path_segment(b'\x6a', b'\x00\x00')
        reply = self.connected_cip_dispatcher.get_attribute_all_service(request_path)
        return int.from_bytes(reply.reply_data[2:4], 'little')

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


class EIPConnectionStatus:
    def __init__(self):
        self.connected = False
        self.connecting = False
        self.reconnecting = False
        self._has_session = False
        self.persist_session = False
        self._session_status_observers = []
        self.keep_alive = False
        self.keep_alive_running = False

    def bind_to_session_status(self, callback):
        """
        Observer Pattern: Allow widgets to bind a callback function that will act on reestablished session
        :param callback:
        :return:
        """
        self._session_status_observers.append(callback)

    @property
    def has_session(self):
        return self._has_session

    @has_session.setter
    def has_session(self, value):
        self._has_session = value
        for callback in self._session_status_observers:
            callback()


class MonitoredVariable:

    instance = {}

    def __new__(cls, dispatcher: "NSeriesThreadDispatcher", variable_name,
                refresh_time: float = 0.05, *args, **kwargs):
        if variable_name in MonitoredVariable.instance:
            monitored_object = MonitoredVariable.instance[variable_name]
            if monitored_object.refresh_time > refresh_time:
                monitored_object.refresh_time = refresh_time
            return monitored_object
        else:
            return super(MonitoredVariable, cls).__new__(cls)

    def __init__(self, dispatcher: "NSeriesThreadDispatcher", variable_name,
                 refresh_time: float = 0.05, observers=[]):
        self.variable_name = variable_name
        self.dispatcher = dispatcher
        self.monitored_variable_observers = observers
        self.refresh_time = refresh_time
        self.refresh_timer = threading.Timer(self.refresh_time, self.update)
        self._value = None
        MonitoredVariable.instance[self.variable_name] = self
        self.update()

    def bind_to_value(self, callback):
        """
        Observer Pattern: Allow widgets to bind a callback function that will act on value change
        :param callback:
        :return:
        """
        self.monitored_variable_observers.append(callback)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.dispatcher.verified_write_variable(self.variable_name, value)
        self._value = value
        for callback in self.monitored_variable_observers:
            callback()

    def update(self):
        temp_value = self._value
        self._value = self.dispatcher.read_variable(self.variable_name)
        if temp_value != self._value:
            for callback in self.monitored_variable_observers:
                callback()
        self.refresh_timer = threading.Timer(self.refresh_time, self.update)
        self.refresh_timer.daemon = True
        self.refresh_timer.start()

    def start(self):
        self.refresh_timer.start()

    def cancel(self):
        self.refresh_timer.cancel()


class NSeriesThreadDispatcher:
    def __init__(self):
        self._instance = NSeries()
        self._host = None
        self.message_timeout = 0.5
        self.executor = None
        self.futures = []
        self.status_integer = 0
        self.services = None
        self.monitored_variable_dictionary = {}
        self.connection_status = EIPConnectionStatus()

    def add_monitored_variable(self, monitored_variable: MonitoredVariable):
        self.monitored_variable_dictionary[monitored_variable.variable_name] = monitored_variable

    def _execute_eip_command(self, command, *args, **kwargs):
        if self.connection_status.connected:
            future = self.executor.submit(command, *args, **kwargs)
            try:
                result = future.result()
                return result
            except socket.error as err:
                print(f'{err} occurred in _execute_eip_command')
                self.connection_status.connected = False
                self.connection_status.keep_alive_running = False
                self.executor.shutdown()
                self._reconnect()
        else:
            self._reconnect()

    def retry_command(self, command, retry_time: float = 0.05, *args, **kwargs):
        reply = command(*args, **kwargs)
        if not reply:
            delay = threading.Timer(retry_time, self.retry_command, command,
                                    *args, **dict(**kwargs, retry_time=retry_time))
            delay.daemon = True
            delay.start()
        return reply

    def _reconnect(self, already_executing=False):
        if not already_executing and not self.connection_status.reconnecting:
            self.connection_status.reconnecting = True
            self._reconnect(already_executing=True)
        elif self.connection_status.reconnecting and already_executing:
            if not self.connection_status.connected:
                try:
                    self.close_explicit()
                except Exception as err:
                    print(f'{err} occurred in close_explicit')
                self.connect_explicit(self._host)
                self._reconnect(already_executing=True)
            if (self.connection_status.persist_session
                    and self.connection_status.connected
                    and not self.connection_status.has_session):
                self.register_session()
                self._reconnect(already_executing=True)
            elif not self.connection_status.persist_session and not self.connection_status.keep_alive:
                self.connection_status.reconnecting = False
            if self.connection_status.keep_alive and self.connection_status.has_session:
                self.start_keep_alive()
            elif not self.connection_status.keep_alive:
                self.connection_status.reconnecting = False

    def start_keep_alive(self, keep_alive_time: float = 0.05):
        self.connection_status.keep_alive = True
        if (self.connection_status.connected
                and self.connection_status.keep_alive
                and self.connection_status.has_session):
            self.connection_status._keep_alive_running = True
            self.services = self._execute_eip_command(self._instance.connected_cip_dispatcher.list_services, '')
            delay = threading.Timer(keep_alive_time, self.start_keep_alive, [keep_alive_time])
            delay.daemon = True
            delay.start()

    def connect_explicit(self, host: str, retry_time: float = 1.0):
        self.connection_status.connecting = True
        if not self.connection_status.connected:
            self._host = host
            try:
                self._instance.connect_explicit(host=self._host)
                self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                self.connection_status.connected = self._instance.connected_cip_dispatcher.is_connected_explicit
                self.connection_status.connecting = False
            except socket.error as err:
                print(f"Failed to connect, trying again in {retry_time} seconds")
                delay = threading.Timer(retry_time, self.connect_explicit, [host, retry_time])
                delay.start()

    def register_session(self, retry_time: float = 1.0):
        self._instance.register_session()
        session_id = self._instance.connected_cip_dispatcher.session_handle_id
        if session_id != b'\x00\x00\x00\x00\x00\x00\x00\x00':
            self.connection_status.has_session = True
        else:
            print(f"Failed to register session, trying again in {retry_time} seconds")
            delay = threading.Timer(retry_time, self.register_session, [retry_time])
            delay.start()
        self.connection_status.persist_session = True

    def unregister_session(self):
        self.connection_status.has_session = False
        self.connection_status.persist_session = False

    def update_variable_dictionary(self):
        self._instance.update_variable_dictionary()

    def save_current_dictionary(self, file_name: str):
        self._instance.save_current_dictionary(file_name)

    def load_dictionary_file(self, file_name: str):
        self._instance.load_dictionary_file(file_name)

    def load_dictionary_file_if_present(self, file_name: str):
        self._instance.load_dictionary_file_if_present(file_name)

    def read_variable(self, variable_name: str):
        try:
            return self._execute_eip_command(self._instance.read_variable, variable_name)
        except struct.error as err:
            pass

    def write_variable(self, variable_name: str, data):
        return self._execute_eip_command(self._instance.write_variable, variable_name, data)

    def verified_write_variable(self, variable_name: str, data):
        try:
            return self._execute_eip_command(self._instance.verified_write_variable, variable_name, data)
        except struct.error as error:
            raise error

    def close_explicit(self):
        self.connection_status.connected = False
        self.connection_status.has_session = False
        self.connection_status._keep_alive_running = False
        for monitored in self.monitored_variable_dictionary:
            self.monitored_variable_dictionary[monitored].cancel()
        time.sleep(0.01)
        self.executor.shutdown(wait=True)
        if self._instance.connected_cip_dispatcher.is_connected_explicit:
            self._instance.close_explicit()

    def __enter__(self):
        signal(SIGINT, self._sigint_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_explicit()

    def _sigint_handler(self, signal_received, frame):
        print('Program interrupted with Ctrl+C')
        self.__exit__(None, None, None)
        sys.exit(0)
