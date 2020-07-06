__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket
import binascii
from typing import List


class CIPRequest:
    """

    1756-pm020_-en-p.pdf 17 of 94

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

    def __init__(self, request_service: bytes, request_path: bytes, request_data: bytes = b''):
        """

        :param request_service: bytes
        :param request_path: bytes
        :param request_data: bytes
        """
        self.request_service = request_service
        self.request_data = request_data
        # Length is in Words, so the byte length is divided in half
        self.request_path_size = len(request_path) // 2
        self.request_path = request_path

    @staticmethod
    def tag_request_path(tag_name: str) -> bytes:
        request_path_bytes = b'\x91' + len(tag_name).to_bytes(1, 'little') + tag_name.encode('utf-8')
        if len(request_path_bytes) % 2 != 0:
            request_path_bytes = request_path_bytes + b'\x00'
        return request_path_bytes

    def bytes(self):
        return self.request_service + self.request_path_size.to_bytes(1, 'little') + \
               self.request_path + self.request_data


class CIPReply:
    def __init__(self, reply_bytes: bytes):
        self.reply_service = reply_bytes[0:1]
        self.reserved = reply_bytes[1:2]
        self.general_status = reply_bytes[2:3]
        self.extended_status_size = reply_bytes[3:4]
        # TODO Research any replies that use this. It's usually zero, so I am guessing it is in words
        extended_status_byte_offset = int.from_bytes(self.extended_status_size, 'little') * 2
        self.extended_status = reply_bytes[4:extended_status_byte_offset]
        self.reply_data = reply_bytes[4+extended_status_byte_offset:len(reply_bytes)]

    def value(self):
        pass


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
        self.type_id = type_id
        self.length = len(data).to_bytes(2, 'little')
        self.data = data

    def from_bytes(self, bytes_data_address_item: bytes):
        self.type_id = bytes_data_address_item[0:2]
        self.length = bytes_data_address_item[2:4]
        self.data = bytes_data_address_item[4:]

    def bytes(self):
        return self.type_id + self.length + self.data


class CommonPacketFormat:
    def __init__(self, packets: List[DataAndAddressItem]):
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
        self.item_count = int.from_bytes(bytes_common_packet_format[0:2], 'little')
        self.packet_bytes = bytes_common_packet_format[2:]
        packet_offset = 0
        packet_index = 0
        while packet_offset < len(self.packet_bytes):
            data_address_item_id = self.packet_bytes[packet_offset: packet_offset+2]
            data_address_item_length = int.from_bytes(self.packet_bytes[packet_offset+2: packet_offset+4], 'little')
            data_address_item_data = self.packet_bytes[packet_offset+4: packet_offset+data_address_item_length]
            self.packets[packet_index] = DataAndAddressItem(data_address_item_id, data_address_item_data)
            packet_offset = packet_offset + 4 + data_address_item_length
            packet_index = packet_index + 1

    def bytes(self):
        return self.item_count.to_bytes(2, 'little') + self.packet_bytes


class CommandSpecificData:
    def __init__(self, interface_handle: bytes = b'\x00\x00\x00\x00',
                 timeout: bytes = b'\x08\x00',
                 encapsulated_packet: bytes = b''):
        self.interface_handle = interface_handle
        self.timeout = timeout
        self.encapsulated_packet = encapsulated_packet

    def from_bytes(self, bytes_command_specific_data: bytes):
        self.interface_handle = bytes_command_specific_data[0:4]
        self.timeout = bytes_command_specific_data[4:6]
        self.encapsulated_packet = bytes_command_specific_data[6:]

    def bytes(self):
        return self.interface_handle + self.timeout + self.encapsulated_packet


class EIPMessage:
    """
    EIP Message
    |-Command Specific Data
      |-Common Packet Format
        |-Data And Address Item
          |-CIP Message
            |-Route Path
    """
    def __init__(self, command=b'\x00\x00', command_data=b'', session_handle_id=b'\x00\x00\x00\x00',
                 status=b'\x00\x00\x00\x00', sender_context_data=b'\x00\x00\x00\x00\x00\x00\x00\x00',
                 command_options=b'\x00\x00\x00\x00'):
        self.command = command
        self.length = len(command_data).to_bytes(2, 'little')
        self.session_handle_id = session_handle_id
        self.status = status
        self.sender_context_data = sender_context_data
        self.command_options = command_options
        self.command_data = command_data

    def bytes(self):
        return self.command + self.length + self.session_handle_id + self.status + self.sender_context_data + \
               self.command_options + self.command_data

    def from_bytes(self, eip_message_bytes: bytes):
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
        self.is_connected_explicit = False
        self.has_session_handle = False
        if self.explicit_message_socket:
            self.explicit_message_socket.close()

    def send_command(self, eip_command: EIPMessage) -> EIPMessage:
        # TODO move to EIPMessage bytes and from bytes method
        received_eip_message = EIPMessage()
        if self.is_connected_explicit:
            self.explicit_message_socket.send(eip_command.bytes())
            received_data = self.explicit_message_socket.recv(self.BUFFER_SIZE)
            received_eip_message.from_bytes(received_data)
        return received_eip_message

    def read_tag(self, tag_name: str):
        request_path = CIPRequest.tag_request_path(tag_name)
        cip_message = CIPRequest(CIPRequest.READ_TAG_SERVICE, request_path, b'\x01\x00')
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, cip_message.bytes())
        packets = [data_address_item]
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        return self.send_rr_data(command_specific_data.bytes())

    def send_rr_data(self, command_specific_data: bytes):
        eip_message = EIPMessage(b'\x6f\x00', command_specific_data, self.session_handle_id)
        return self.send_command(eip_message).command_data

    def list_services(self):
        eip_message = EIPMessage(b'\x04\x00')
        return self.send_command(eip_message).command_data

    def list_identity(self):
        eip_message = EIPMessage(b'\x63\x00')
        return self.send_command(eip_message).command_data

    def list_interfaces(self):
        eip_message = EIPMessage(b'\x64\x00')
        return self.send_command(eip_message).command_data

    def register_session(self, command_data=b'\x01\x00\x00\x00'):
        eip_message = EIPMessage(b'\x65\x00', command_data)
        response = self.send_command(eip_message)
        self.has_session_handle = True
        self.session_handle_id = response.session_handle_id
        return response

    def get_variable(self, route_path, command_data=b''):
        cip_message = CIPRequest(b'\x01',
                                 route_path, b'')
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, cip_message.bytes())
        packets = [data_address_item]
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        return self.send_rr_data(command_specific_data.bytes())

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
