__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket
import aphytcip


class NXMessageDispatcher:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sequence_number = 0

    def __del__(self):
        self.tcp_socket.close()

    def connect(self, ip_address: str = '192.168.250.1', port: int = 64000):
        self.tcp_socket.connect((ip_address, port))

    def get_input_data_size(self):
        cip_message = aphytcip.cipmessage.CipMessage(b'\x0e', b'\x74\x00', b'\x01\x00',
                                                     b'\x02\x00', self.sequence_number)
        self.tcp_socket.send(cip_message.command)
        response_bytes = self.tcp_socket.recv(512)
        response = aphytcip.cipresponse.CipResponse(response_bytes)
        self.sequence_number += 1
        return response

    def get_output_data_size(self):
        cip_message = aphytcip.cipmessage.CipMessage(b'\x0e', b'\x74\x00', b'\x01\x00',
                                                     b'\x01\x00', self.sequence_number)
        self.tcp_socket.send(cip_message.command)
        response_bytes = self.tcp_socket.recv(512)
        response = aphytcip.cipresponse.CipResponse(response_bytes)
        self.sequence_number += 1
        return response

    def get_input_data(self):
        pass

    def get_output_data(self):
        pass

    def set_output_data(self):
        pass

    def clear_nx_status(self):
        pass

    def change_nx_state(self):
        pass
