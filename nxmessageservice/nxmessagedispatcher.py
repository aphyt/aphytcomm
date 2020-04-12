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

    def execute_cip_command(self, service_code, class_id, instance_id, attribute_id, data=b''):
        cip_message = aphytcip.cipmessage.CipMessage(service_code, class_id, instance_id,
                                                     attribute_id, self.sequence_number, data)
        self.tcp_socket.send(cip_message.command)
        response_bytes = self.tcp_socket.recv(512)
        response = aphytcip.cipresponse.CipResponse(response_bytes)
        self.sequence_number += 1
        return response

    def get_input_data_size(self):
        response = self.execute_cip_command(b'\x0e', b'\x74\x00', b'\x01\x00', b'\x02\x00')
        return response

    def get_output_data_size(self):
        response = self.execute_cip_command(b'\x0e', b'\x74\x00', b'\x01\x00', b'\x01\x00')
        return response

    def get_input_data(self):
        response = self.execute_cip_command(b'\x0e', b'\x04\x00', b'\x64\x00', b'\x03\x00')
        return response

    def get_output_data(self):
        response = self.execute_cip_command(b'\x0e', b'\x04\x00', b'\x94\x00', b'\x03\x00')
        return response

    def set_output_data(self, data):
        response = self.execute_cip_command(b'\x10', b'\x04\x00', b'\x94\x00', b'\x03\x00')
        return response

    def clear_nx_error_status(self):
        response = self.execute_cip_command(b'\x32', b'\x74\x00', b'\x01\x00', b'\x00\x00')
        return response

    def change_nx_state(self):
        response = self.execute_cip_command(b'\x39', b'\x74\x00', b'\x01\x00', b'\x00\x00')
        return response
