__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket


class EIPMessage:
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


class EIP:
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
        received_eip_message = EIPMessage()
        command_bytes = \
            eip_command.command + eip_command.length + eip_command.session_handle_id + \
            eip_command.status + eip_command.sender_context_data + eip_command.command_options + \
            eip_command.command_data
        if self.is_connected_explicit:
            self.explicit_message_socket.send(command_bytes)
            received_data = self.explicit_message_socket.recv(self.BUFFER_SIZE)
            received_eip_message.command = received_data[0:2]
            received_eip_message.length = received_data[2:4]
            received_eip_message.session_handle_id = received_data[4:8]
            received_eip_message.status = received_data[8:12]
            received_eip_message.sender_context_data = received_data[12:20]
            received_eip_message.command_options = received_data[20:24]
            received_eip_message.command_data = received_data[24:]
        return received_eip_message

    # TODO Create NJ CIP message format to use in this method
    '''
    This method adds x0100 to the end of the tag which means Route Path (Port 1 address 0)
    1 is the backplane port, 0 is the CPU unit address.
    '''

    def read_tag(self, tag_name: str):
        tag_char_count = len(tag_name)
        if len(tag_name) % 2 == 0:
            tag_bytes = tag_name.encode('utf-8') + b'\x01\x00'
        else:
            tag_bytes = tag_name.encode('utf-8') + b'\x00\x01\x00'
        word_count = len(tag_bytes) // 2
        tag_bytes = b'\x4c' + word_count.to_bytes(1, 'little') + b'\x91' + tag_char_count.to_bytes(1,
                                                                                                   'little') + tag_bytes
        tag_bytes = b'\x02\x00' + self.null_address_item + b'\xb2\x00' + len(tag_bytes).to_bytes(2,
                                                                                                 'little') + tag_bytes
        tag_bytes = self.cip_handle + b'\x08\x00' + tag_bytes
        feip_message = EIPMessage(b'\x6f\x00', tag_bytes, self.session_handle_id)
        return self.send_command(feip_message).command_data

    def list_services(self):
        eip_message = EIPMessage(b'\x04\x00')
        return self.send_command(eip_message)

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

    def get_instance_attribute_list(self, command_data=b''):
        eip_message = EIPMessage(b'\x6f\x00', b'\x55\x03\x00\x00\x20\x6B\x25\x00\x00\x00\x02\x00\x01\x00\x02\x00', self.session_handle_id)
        response = self.send_command(eip_message)
        return response.status

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
