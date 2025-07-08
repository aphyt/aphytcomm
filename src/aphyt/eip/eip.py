__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import asyncio
import binascii
import socket
import time
from typing import List, Tuple
from aphyt.cip import *


class DataAndAddressItem:
    """
    Data and address items store the data used in common packet format
    EIP-CIP-V2-1.0.pdf Table 2-7.2 – Data and Address item format
    """
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
    """
    Common Packet Format stores the Data and Address packets. Used in both requests and replies.
    """

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
            data_address_item_id = self.packet_bytes[packet_offset: packet_offset + 2]
            data_address_item_length = int.from_bytes(self.packet_bytes[packet_offset + 2: packet_offset + 4], 'little')
            data_address_item_data = self.packet_bytes[packet_offset + 4: packet_offset + data_address_item_length + 4]
            self.packets[packet_index] = DataAndAddressItem(data_address_item_id, data_address_item_data)
            packet_offset = packet_offset + data_address_item_length + 4
            packet_index = packet_index + 1

    def bytes(self):
        return self.item_count.to_bytes(2, 'little') + self.packet_bytes


class CommandSpecificData:
    """
    Command Specific Data is sent in an EIP send rr command
    """

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
    Class for creating or parsing Ethernet/IP messages

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
        return \
            self.command + self.length + self.session_handle_id + self.status + \
            self.sender_context_data + self.command_options + self.command_data

    def from_bytes(self, eip_message_bytes: bytes):
        self.command = eip_message_bytes[0:2]
        self.length = eip_message_bytes[2:4]
        self.session_handle_id = eip_message_bytes[4:8]
        self.status = eip_message_bytes[8:12]
        self.sender_context_data = eip_message_bytes[12:20]
        self.command_options = eip_message_bytes[20:24]
        self.command_data = eip_message_bytes[24:]

    def context_integer(self):
        return struct.unpack('<Q', self.sender_context_data)[0]

    def set_context(self, value: int):
        self.sender_context_data = struct.pack('<Q', value)

    def total_length(self):
        return struct.unpack('<H', self.length)[0] + 24


class EIPDispatcher(ABC):
    explicit_message_port = 44818

    def __init__(self):
        super().__init__()
        self.socket = None
        self.eip_responses = {}
        self.message_number = 18446744073709551613 # Using a number close to the max, fail fast on rollover errors

    @abstractmethod
    def send_command(self, eip_command: EIPMessage, host: str) -> EIPMessage:
        pass

    def list_identity(self, host=''):
        """
        Used by an originator to locate possible targets
        :return:
        """
        eip_message = EIPMessage(b'\x63\x00')
        return self.send_command(eip_message, host).command_data

    def list_services(self, host=''):
        """
        Find which services a target supports
        :return:
        """
        eip_message = EIPMessage(b'\x04\x00')
        return self.send_command(eip_message, host).command_data

    def list_interfaces(self, host=''):
        """
        Used by an originator to identify possible non-CIP interfaces on the target
        :return:
        """
        eip_message = EIPMessage(b'\x64\x00')
        return self.send_command(eip_message, host).command_data


class AsyncEIPDispatcher(ABC):
    explicit_message_port = 44818

    def __init__(self):
        super().__init__()
        self.socket = None
        self.eip_responses = {}
        self.message_number = 18446744073709551613 # Using a number close to the max, fail fast on rollover errors

    @abstractmethod
    async def send_command(self, eip_command: EIPMessage, host: str) -> EIPMessage:
        pass

    async def list_identity(self, host=''):
        """
        Used by an originator to locate possible targets
        :return:
        """
        eip_message = EIPMessage(b'\x63\x00')
        return await self.send_command(eip_message, host).command_data

    async def list_services(self, host=''):
        """
        Find which services a target supports
        :return:
        """
        eip_message = EIPMessage(b'\x04\x00')
        return await self.send_command(eip_message, host).command_data

    async def list_interfaces(self, host=''):
        """
        Used by an originator to identify possible non-CIP interfaces on the target
        :return:
        """
        eip_message = EIPMessage(b'\x64\x00')
        return await self.send_command(eip_message, host).command_data


class AsyncEIPConnectedCommandMixin(AsyncEIPDispatcher):
    lock = asyncio.Lock()
    def __init__(self):
        super().__init__()
        self.explicit_message_socket = None
        self.stream_writer = None
        self.stream_reader = None
        self.session_handle_id = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self.is_connected_explicit = False
        self.has_session_handle = False
        self.BUFFER_SIZE = 4096
        self.host = None

    async def get_response(self, eip_message: EIPMessage):
        if eip_message.context_integer() in self.eip_responses.keys():
            result = self.eip_responses.pop(eip_message.context_integer())
            return result
        else:
            self.stream_writer.write(eip_message.bytes())
            await self.stream_writer.drain()
            time.sleep(.0004)
            async with AsyncEIPConnectedCommandMixin.lock:
                # await asyncio.sleep(.00001)
                received_data = await self.stream_reader.readexactly(n=24)
                received_data += await self.stream_reader.readexactly(n=struct.unpack('<H',received_data[2:4])[0])
            length = struct.unpack('<H',received_data[2:4])[0] + 24
            received_eip_message = EIPMessage()
            # while len(received_data) > length:
            #     received_eip_message.from_bytes(received_data[0:length])
            #     received_data = received_data[length:]
            #     length = struct.unpack('<H', received_data[2:4])[0] + 24
            #     self.eip_responses[received_eip_message.context_integer()] = received_eip_message
            received_eip_message.from_bytes(received_data[0:length])
            # received_eip_message.from_bytes(received_data)
            self.eip_responses[received_eip_message.context_integer()] = received_eip_message
            return await self.get_response(eip_message)


    async def send_command(self, eip_command: EIPMessage, host) -> EIPMessage:
        """
        Used to send and receive Ethernet/IP messages
        :param host:
        :param eip_command:
        :return:
        """
        # received_eip_message = EIPMessage()
        if self.message_number == 18446744073709551616:
            self.message_number = 0
        eip_command.set_context(self.message_number)
        self.message_number = self.message_number + 1
        return await self.get_response(eip_command)

    async def connect_explicit(self, host, connection_timeout: float = None):
        """
        Create and explicit Ethernet/IP connection
        :param connection_timeout:
        :param host:
        """
        try:
            self.stream_reader, self.stream_writer = (
                await asyncio.open_connection(host, self.explicit_message_port))
            self.host = host
            self.is_connected_explicit = True
        except socket.error as err:
            if self.explicit_message_socket:
                await self.explicit_message_socket.close()
                self.is_connected_explicit = False
            raise err

    async def close_explicit(self):
        """
        Close the explicit Ethernet/IP connection
        :return:
        """
        self.is_connected_explicit = False
        self.has_session_handle = False
        self.host = None
        if self.explicit_message_socket:
            await self.explicit_message_socket.close()

    async def register_session(self, command_data=b'\x01\x00\x00\x00'):
        """
        Used by an originator to establish a session. It is required before sending CIP messages
        :param command_data:
        :return:
        """
        eip_message = EIPMessage(b'\x65\x00', command_data)
        response = await self.send_command(eip_message, self.host)
        self.has_session_handle = True
        self.session_handle_id = response.session_handle_id
        return response


class EIPConnectedCommandMixin(EIPDispatcher):
    def __init__(self):
        super().__init__()
        self.explicit_message_socket = None
        self.session_handle_id = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self.is_connected_explicit = False
        self.has_session_handle = False
        self.BUFFER_SIZE = 4096
        self.host = None

    def __del__(self):
        self.close_explicit()

    def get_response(self, eip_message: EIPMessage):
        if eip_message.context_integer() in self.eip_responses.keys():
            result = self.eip_responses.pop(eip_message.context_integer())
            return result
        else:
            self.explicit_message_socket.send(eip_message.bytes())
            received_data = self.explicit_message_socket.recv(self.BUFFER_SIZE)
            length = struct.unpack('<H',received_data[2:4])[0] + 24
            received_eip_message = EIPMessage()
            while len(received_data) > length:
                received_eip_message.from_bytes(received_data[0:length])
                received_data = received_data[length:]
                length = struct.unpack('<H', received_data[2:4])[0] + 24
                self.eip_responses[received_eip_message.context_integer()] = received_eip_message
            received_eip_message.from_bytes(received_data[0:length])
            if len(received_data) > 0:
                received_eip_message.from_bytes(received_data)
            self.eip_responses[received_eip_message.context_integer()] = received_eip_message
            return self.get_response(eip_message)


    def send_command(self, eip_command: EIPMessage, host) -> EIPMessage:
        """
        Used to send and receive Ethernet/IP messages
        :param host:
        :param eip_command:
        :return:
        """
        # received_eip_message = EIPMessage()
        if self.is_connected_explicit:
            if self.message_number == 18446744073709551616:
                self.message_number = 0
            eip_command.set_context(self.message_number)
            self.message_number = self.message_number + 1
            return self.get_response(eip_command)

    def connect_explicit(self, host, connection_timeout: float = None):
        """
        Create and explicit Ethernet/IP connection
        :param connection_timeout:
        :param host:
        """
        try:
            self.explicit_message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            old_timeout = self.explicit_message_socket.gettimeout()
            if connection_timeout is not None:
                self.explicit_message_socket.settimeout(connection_timeout)
            self.explicit_message_socket.connect((host, self.explicit_message_port))
            self.explicit_message_socket.settimeout(old_timeout)
            self.host = host
            self.is_connected_explicit = True
        except socket.error as err:
            if self.explicit_message_socket:
                self.explicit_message_socket.close()
                self.is_connected_explicit = False
            raise err

    def close_explicit(self):
        """
        Close the explicit Ethernet/IP connection
        :return:
        """
        self.is_connected_explicit = False
        self.has_session_handle = False
        self.host = None
        if self.explicit_message_socket:
            self.explicit_message_socket.close()

    def register_session(self, command_data=b'\x01\x00\x00\x00'):
        """
        Used by an originator to establish a session. It is required before sending CIP messages
        :param command_data:
        :return:
        """
        eip_message = EIPMessage(b'\x65\x00', command_data)
        response = self.send_command(eip_message, self.host)
        self.has_session_handle = True
        self.session_handle_id = response.session_handle_id
        return response


class EIPUnconnectedCommandMixin(EIPDispatcher):
    """
    ToDo add broadcast_command to return a List of EIPMessages (List Service to a full domain)
    """
    def __init__(self):
        super().__init__()

    def send_command(self, eip_command: EIPMessage, host: str) -> List[EIPMessage]:
        received_eip_message = EIPMessage()
        response_list = []
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.settimeout(5)
            print(self.explicit_message_port)
            udp_socket.bind(('0.0.0.0', self.explicit_message_port))
            udp_socket.sendto(eip_command.bytes(), (host, self.explicit_message_port))
            received_data = udp_socket.recvfrom(1024)[0]
            # while True:
            #     try:
            #         received_data = udp_socket.recvfrom(1024)[0]
            #         # response_list.append(received_eip_message.from_bytes(received_data))
            #     except socket.error as e:
            #         break
            received_eip_message.from_bytes(received_data)
        except socket.error as e:
            print('Failed to create socket')
            print(e)

        return received_eip_message


class AsyncEIPConnectedCIPDispatcher(AsyncEIPConnectedCommandMixin, AsyncCIPDispatcher):
    """
    EIP is an encapsulation protocol for CIP (common industrial protocol) messages
    """

    null_address_item = b'\x00\x00\x00\x00'
    cip_handle = b'\x00\x00\x00\x00'

    def __init__(self):
        super().__init__()

    async def execute_cip_command(self, request: CIPRequest) -> CIPReply:
        """
        Implements the abstract method in order to become a concrete CIPDispatcher class
        :param request:
        :return:
        """
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, request.bytes)
        packets = [data_address_item]
        # ToDo add interface handle to track responses?
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        response = await self.send_rr_data(command_specific_data.bytes())
        response = response.packets[1].bytes()
        reply_data_and_address_item = DataAndAddressItem('', b'')
        # ToDo is this removing error data?
        reply_data_and_address_item.from_bytes(response)
        cip_reply = CIPReply(reply_data_and_address_item.data)
        return cip_reply


    async def send_rr_data(self, command_specific_data: bytes) -> CommonPacketFormat:
        """
        Ethernet/IP command to send an encapsulated request and reply packet between originator and target
        :param command_specific_data:
        :return:
        """
        eip_message = EIPMessage(b'\x6f\x00', command_specific_data, self.session_handle_id)
        reply = await self.send_command(eip_message, self.host)
        reply_command_specific_data = CommandSpecificData()
        reply_command_specific_data.from_bytes(reply.command_data)
        reply_packet = CommonPacketFormat([])
        reply_packet.from_bytes(reply_command_specific_data.encapsulated_packet)
        return reply_packet


class EIPConnectedCIPDispatcher(EIPConnectedCommandMixin, CIPDispatcher):
    """
    EIP is an encapsulation protocol for CIP (common industrial protocol) messages
    """

    null_address_item = b'\x00\x00\x00\x00'
    cip_handle = b'\x00\x00\x00\x00'

    def __init__(self):
        super().__init__()

    def execute_cip_command(self, request: CIPRequest) -> CIPReply:
        """
        Implements the abstract method in order to become a concrete CIPDispatcher class
        :param request:
        :return:
        """
        data_address_item = DataAndAddressItem(DataAndAddressItem.UNCONNECTED_MESSAGE, request.bytes)
        packets = [data_address_item]
        # ToDo add interface handle to track responses?
        common_packet_format = CommonPacketFormat(packets)
        command_specific_data = CommandSpecificData(encapsulated_packet=common_packet_format.bytes())
        response = self.send_rr_data(command_specific_data.bytes()).packets[1].bytes()
        reply_data_and_address_item = DataAndAddressItem('', b'')
        # ToDo is this removing error data?
        reply_data_and_address_item.from_bytes(response)
        cip_reply = CIPReply(reply_data_and_address_item.data)
        return cip_reply

    # @staticmethod
    # def command_specific_data_from_eip_message_bytes(eip_message_bytes: bytes):
    #     """
    #     Extracts command specific data from Ethernet/IP reply bytes
    #     :param eip_message_bytes:
    #     :return:
    #     """
    #     eip_message = EIPMessage()
    #     eip_message.from_bytes(eip_message_bytes)
    #     return EIPConnectedCIPDispatcher.command_specific_data_from_eip_message(eip_message)
    #
    # @staticmethod
    # def command_specific_data_from_eip_message(eip_message: EIPMessage) -> CommandSpecificData:
    #     """
    #     Extracts the command specific data from an Ethernet/IP message
    #     :param eip_message:
    #     :return:
    #     """
    #     command_specific_data = CommandSpecificData()
    #     command_specific_data.from_bytes(eip_message.bytes())
    #     return command_specific_data

    def send_rr_data(self, command_specific_data: bytes) -> CommonPacketFormat:
        """
        Ethernet/IP command to send an encapsulated request and reply packet between originator and target
        :param command_specific_data:
        :return:
        """
        eip_message = EIPMessage(b'\x6f\x00', command_specific_data, self.session_handle_id)
        reply = self.send_command(eip_message, self.host)
        reply_command_specific_data = CommandSpecificData()
        reply_command_specific_data.from_bytes(reply.command_data)
        reply_packet = CommonPacketFormat([])
        reply_packet.from_bytes(reply_command_specific_data.encapsulated_packet)
        return reply_packet

    # def get_attribute_all_service(self, tag_request_path):
    #     get_attribute_all_request = CIPRequest(CIPService.GET_ATTRIBUTE_ALL, tag_request_path)
    #     return self.execute_cip_command(get_attribute_all_request)
    #
    # def get_attribute_single_service(self, tag_request_path):
    #     get_attribute_single_request = CIPRequest(CIPService.GET_ATTRIBUTE_SINGLE, tag_request_path)
    #     return self.execute_cip_command(get_attribute_single_request)
