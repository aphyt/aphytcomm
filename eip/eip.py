__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket
from typing import List

from eip.cip import CIPRequest, CIPReply, CIPDataTypes, address_request_path_segment, variable_request_path_segment


class DataAndAddressItem:
    """EIP-CIP-V2-1.0.pdf Table 2-7.2 – Data and Address item format"""
    NULL_ADDRESS_ITEM = b'\x00\x00'
    CONNECTED_TRANSPORT_PACKET = b'\xb1\x00'
    UNCONNECTED_MESSAGE = b'\xb2\x00'
    LIST_SERVICES_RESPONSE = b'\x00\x01'
    SOCKADDR_INFO_ORIGINATOR_TO_TARGET = b'\x00\x80'
    SOCKADDR_INFO_TARGET_TO_ORIGINATOR = b'\x01\x80'
    SEQUENCED_ADDRESS_ITEM = b'\x02\x80'

    def __init__(self, type_id, data: bytes):
        """

        :param type_id:
        :param data:
        """
        self.type_id = type_id
        self.length = len(data).to_bytes(2, 'little')
        self.data = data

    def from_bytes(self, bytes_data_address_item: bytes):
        """

        :param bytes_data_address_item:
        :return:
        """
        self.type_id = bytes_data_address_item[0:2]
        self.length = bytes_data_address_item[2:4]
        self.data = bytes_data_address_item[4:]

    def bytes(self):
        """

        :return:
        """
        return self.type_id + self.length + self.data


class CommonPacketFormat:
    """
    Common Packet Format stores the Data and Address packets. Used in both requests and replies.
    """

    def __init__(self, packets: List[DataAndAddressItem]):
        """

        :param packets:
        """
        self.packets = [DataAndAddressItem(DataAndAddressItem.NULL_ADDRESS_ITEM, b''),
                        DataAndAddressItem(DataAndAddressItem.NULL_ADDRESS_ITEM, b'')]
        if len(packets) < 1:
            pass
        elif len(packets) < 2:
            self.packets[1] = packets[0]
        else:
            self.packets = packets
        self.item_count = len(self.packets)
        self.packet_bytes = b''
        for packet in self.packets:
            self.packet_bytes += packet.bytes()

    def from_bytes(self, bytes_common_packet_format: bytes):
        """

        :param bytes_common_packet_format:
        :return:
        """
        self.item_count = int.from_bytes(bytes_common_packet_format[0:2], 'little')
        self.packet_bytes = bytes_common_packet_format[2:]
        packet_offset = 0
        packet_index = 0
        while packet_offset < len(self.packet_bytes):
            data_address_item_id = self.packet_bytes[packet_offset: packet_offset + 2]
            data_address_item_length = int.from_bytes(self.packet_bytes[packet_offset + 2: packet_offset + 4], 'little')
            data_address_item_data = self.packet_bytes[packet_offset + 4: packet_offset + data_address_item_length + 4]
            self.packets[packet_index] = DataAndAddressItem(data_address_item_id, data_address_item_data)
            packet_offset = packet_offset + data_address_item_length + 4
            packet_index = packet_index + 1

    def bytes(self):
        """

        :return:
        """
        return self.item_count.to_bytes(2, 'little') + self.packet_bytes


class CommandSpecificData:
    """
    Command Specific Data is sent in an EIP send rr command
    """

    def __init__(self, interface_handle: bytes = b'\x00\x00\x00\x00',
                 timeout: bytes = b'\x08\x00',
                 encapsulated_packet: bytes = b''):
        """

        :param interface_handle:
        :param timeout:
        :param encapsulated_packet:
        """
        self.interface_handle = interface_handle
        self.timeout = timeout
        self.encapsulated_packet = encapsulated_packet

    def from_bytes(self, bytes_command_specific_data: bytes):
        """

        :param bytes_command_specific_data:
        :return:
        """
        self.interface_handle = bytes_command_specific_data[0:4]
        self.timeout = bytes_command_specific_data[4:6]
        self.encapsulated_packet = bytes_command_specific_data[6:]

    def bytes(self):
        """

        :return:
        """
        return self.interface_handle + self.timeout + self.encapsulated_packet


class EIPMessage:
    """

    EIP Message::
        |-Command Specific Data
          |-Common Packet Format
            |-Data And Address Item
              |-CIP Message
                |-Route Path
    """

    def __init__(self, command=b'\x00\x00', command_data=b'', session_handle_id=b'\x00\x00\x00\x00',
                 status=b'\x00\x00\x00\x00', sender_context_data=b'\x00\x00\x00\x00\x00\x00\x00\x00',
                 command_options=b'\x00\x00\x00\x00'):
        """

        :param command:
        :param command_data:
        :param session_handle_id:
        :param status:
        :param sender_context_data:
        :param command_options:
        """
        self.command = command
        self.length = len(command_data).to_bytes(2, 'little')
        self.session_handle_id = session_handle_id
        self.status = status
        self.sender_context_data = sender_context_data
        self.command_options = command_options
        self.command_data = command_data

    def bytes(self) -> bytes:
        """

        :return:
        """
        return self.command + self.length + self.session_handle_id + self.status + self.sender_context_data + \
               self.command_options + self.command_data

    def from_bytes(self, eip_message_bytes: bytes):
        """

        :param eip_message_bytes:
        :return:
        """
        self.command = eip_message_bytes[0:2]
        self.length = eip_message_bytes[2:4]
        self.session_handle_id = eip_message_bytes[4:8]
        self.status = eip_message_bytes[8:12]
        self.sender_context_data = eip_message_bytes[12:20]
        self.command_options = eip_message_bytes[20:24]
        self.command_data = eip_message_bytes[24:]


class EIP:
    """
    EIP
    """
    explicit_message_port = 44818
    null_address_item = b'\x00\x00\x00\x00'
    cip_handle = b'\x00\x00\x00\x00'

    def __init__(self):
        """


        """
        self.explicit_message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session_handle_id = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self.is_connected_explicit = False
        self.has_session_handle = False
        self.variables = {}
        self.user_variables = {}
        self.system_variables = {}
        self.BUFFER_SIZE = 4096

    def __del__(self):
        self.close_explicit()

    def connect_explicit(self, host):
        """

        :param host:
        """
        try:
            self.explicit_message_socket.connect((host, self.explicit_message_port))
            self.is_connected_explicit = True
        except socket.error as err:
            if self.explicit_message_socket:
                self.explicit_message_socket.close()
                self.is_connected_explicit = False

    def close_explicit(self):
        """

        :return:
        """
        self.is_connected_explicit = False
        self.has_session_handle = False
        if self.explicit_message_socket:
            self.explicit_message_socket.close()

    @staticmethod
    def command_specific_data_from_eip_message_bytes(eip_message_bytes: bytes):
        """

        :param eip_message_bytes:
        :return:
        """
        eip_message = EIPMessage()
        eip_message.from_bytes(eip_message_bytes)
        return EIP.command_specific_data_from_eip_message(eip_message)

    @staticmethod
    def command_specific_data_from_eip_message(eip_message: EIPMessage) -> CommandSpecificData:
        """

        :param eip_message:
        :return:
        """
        command_specific_data = CommandSpecificData()
        command_specific_data.from_bytes(eip_message.bytes())
        return command_specific_data

    @staticmethod
    def cip_reply_from_eip_message_bytes(eip_message_bytes: bytes) -> CIPReply:
        """

        :param eip_message_bytes:
        :return:
        """
        eip_message = EIPMessage()
        eip_message.from_bytes(eip_message_bytes)
        return EIP.cip_reply_from_eip_message(eip_message)

    @staticmethod
    def cip_reply_from_eip_message(eip_message: EIPMessage) -> CIPReply:
        """

        :param eip_message:
        :return:
        """
        command_specific_data = CommandSpecificData()
        command_specific_data.from_bytes(eip_message.command_data)
        common_packet_format = CommonPacketFormat([])
        common_packet_format.from_bytes(command_specific_data.bytes())
        cip_reply = CIPReply(common_packet_format.packets[1].bytes())
        return cip_reply

    def send_command(self, eip_command: EIPMessage) -> EIPMessage:
        """

        :param eip_command:
        :return:
        """
        # TODO move to EIPMessage bytes and from bytes method
        received_eip_message = EIPMessage()
        if self.is_connected_explicit:
            self.explicit_message_socket.send(eip_command.bytes())
            received_data = self.explicit_message_socket.recv(self.BUFFER_SIZE)
            received_eip_message.from_bytes(received_data)
        return received_eip_message

    def read_variable(self, variable_name: str):
        cip_data_type = self._get_variable_with_cip_data_type(variable_name=variable_name)
        return cip_data_type.value()

    def write_variable(self, variable_name: str, data, additional_info: bytes = b''):
        cip_data_type = self.variables.get(variable_name)
        cip_data = CIPDataTypes()
        cip_data.from_value(data, cip_data_type, additional_info)
        request_path = variable_request_path_segment(variable_name)
        data_bytes = cip_data.data_type_code + cip_data.addition_info_length.to_bytes(1, 'little') + b'\x01\x00' + cip_data.data
        cip_message = CIPRequest(CIPRequest.WRITE_TAG_SERVICE, request_path, data_bytes)
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, cip_message.bytes())
        packets = [data_address_item]
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        # Response will a common packet format and the index 1 will contain the data
        response = self.send_rr_data(command_specific_data.bytes()).packets[1].bytes()
        return response

    def _get_variable_with_cip_data_type(self, variable_name: str):
        """
        ToDo Currently just reading symbolic. Add Logical Segment (Class Instance Attribute)
        :param variable_name:
        :return:
        """
        request_path = variable_request_path_segment(variable_name)
        cip_message = CIPRequest(CIPRequest.READ_TAG_SERVICE, request_path, b'\x01\x00')
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, cip_message.bytes())
        packets = [data_address_item]
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        response = self.send_rr_data(command_specific_data.bytes()).packets[1].bytes()
        reply_data_and_address_item = DataAndAddressItem('', b'')
        reply_data_and_address_item.from_bytes(response)
        cip_reply = CIPReply(reply_data_and_address_item.data)
        cip_data_type = CIPDataTypes()
        cip_data_type.from_bytes(cip_reply.reply_data)
        return cip_data_type

    def send_rr_data(self, command_specific_data: bytes) -> CommonPacketFormat:
        """

        :param command_specific_data:
        :return:
        """
        eip_message = EIPMessage(b'\x6f\x00', command_specific_data, self.session_handle_id)
        reply = self.send_command(eip_message)
        reply_command_specific_data = CommandSpecificData()
        reply_command_specific_data.from_bytes(reply.command_data)
        reply_packet = CommonPacketFormat([])
        reply_packet.from_bytes(reply_command_specific_data.encapsulated_packet)
        return reply_packet

    def list_services(self):
        """

        :return:
        """
        eip_message = EIPMessage(b'\x04\x00')
        return self.send_command(eip_message).command_data

    def list_identity(self):
        """

        :return:
        """
        eip_message = EIPMessage(b'\x63\x00')
        return self.send_command(eip_message).command_data

    def list_interfaces(self):
        """

        :return:
        """
        eip_message = EIPMessage(b'\x64\x00')
        return self.send_command(eip_message).command_data

    def register_session(self, command_data=b'\x01\x00\x00\x00'):
        """

        :param command_data:
        :return:
        """
        eip_message = EIPMessage(b'\x65\x00', command_data)
        response = self.send_command(eip_message)
        self.has_session_handle = True
        self.session_handle_id = response.session_handle_id
        return response

    def update_variable_dictionary(self):
        """

        :return:
        """
        variable_list = self._get_variable_list()
        for variable in variable_list:
            variable_response_bytes = self._get_variable_with_cip_data_type(variable)
            self.variables.update({variable: variable_response_bytes.data_type_code})
            if variable[0:1] == '_':
                self.system_variables.update({variable: variable_response_bytes.data_type_code})
            else:
                self.user_variables.update({variable: variable_response_bytes.data_type_code})

    def _get_attribute_all(self, route_path: bytes):
        pass

    def _get_attribute_single(self, route_path: bytes):
        pass

    def _get_request_route_path(self, route_path: bytes):
        """

        :param route_path:
        :return:
        """
        # ToDo eliminate with a get_attribute_all method
        cip_message = CIPRequest(b'\x01',
                                 route_path, b'')
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, cip_message.bytes())
        packets = [data_address_item]
        request_common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=request_common_packet_format.bytes())
        response = self.send_rr_data(command_specific_data.bytes()).packets[1].bytes()
        return response

    def _get_variable_list(self):
        """

        :return:
        """
        tag_list = []
        for tag_index in range(self._get_number_of_variables()):
            offset = tag_index + 1
            route_path = address_request_path_segment(b'\x6a', offset.to_bytes(2, 'little'))
            response = self._get_request_route_path(route_path)
            tag = str(response[13:13 + int.from_bytes(response[12:13], 'little')], 'utf-8')
            tag_list.append(tag)
        return tag_list

    def _get_number_of_variables(self) -> int:
        """
        Find number of variables from Tag Name Server
        :return:
        """
        route_path = address_request_path_segment(b'\x6a', b'\x00\x00')
        reply = self._get_request_route_path(route_path)
        return int.from_bytes(reply[10:12], 'little')

    # feip_commands = FEIPCommands(
    #     nop=CodeDescription(b'\x00\x00',
    #                         'A non-operational command used during TCP communications to verify TCP connection'),
    #     list_services=CodeDescription(b'\x00\x04', 'List the scanners EtherNet/IP services available'),
    #     list_identity=CodeDescription(b'\x00\x63', 'List the scanners EtherNet/IP identity, vendor ID,device ID, '
    #                                                'serial number and other information'),
    #     list_interfaces=CodeDescription(b'\x00\x64',
    #                                     'List the scanners EtherNet/IP assembly and input/output object'
    #                                     ' interfaces available'),
    #     register_session=CodeDescription(b'\x00\x65', 'Open and register a communication session with the scanner'),
    #     un_register_session=CodeDescription(b'\x00\x66',
    #                                         'Close the registered communication session with the scanner'),
    #     send_rr_data=CodeDescription(b'\x00\x6F',
    #                                  'Send a request/reply command to the scanner along with a sub-command'
    #                                  ' and optional data'))

    # feip_errors = [CodeDescription(b'\x00\x00', 'No error in command request'),
    #                CodeDescription(b'\x00\x01', 'Invalid command used in request'),
    #                CodeDescription(b'\x00\x02', 'Insufficient memory in target device'),
    #                CodeDescription(b'\x00\x03', 'Incorrect data used in request'),
    #                CodeDescription(b'\x00\x64', 'Invalid session handle used in request'),
    #                CodeDescription(b'\x00\x65', 'Invalid command length used in request'),
    #                CodeDescription(b'\x00\x69', 'Unsupported protocol version used in request')]

    # def error_code_to_description(self, code):
    #     for error in self.feip_errors:
    #         if code == error.code:
    #             return error.description
