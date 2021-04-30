__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket
import nxmessaging


class NXMessageDispatcher:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sequence_number = 0

    def __del__(self):
        self.tcp_socket.close()

    def connect(self, ip_address: str = '192.168.250.1', port: int = 64000):
        self.tcp_socket.connect((ip_address, port))

    def disconnect(self):
        try:
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
            self.tcp_socket.close()
        finally:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def execute_command(self, service_code, class_id, instance_id, attribute_id=b'', data=b''):
        cip_message = nxmessaging.nxmessage.CipMessage(service_code, class_id, instance_id,
                                                       attribute_id, self.sequence_number, data)
        self.tcp_socket.send(cip_message.command)
        response_bytes = self.tcp_socket.recv(512)
        response = nxmessaging.nxresponse.CipResponse(response_bytes)
        self.sequence_number += 1
        return response

    def get_all_identity_object_attributes(self):
        response = self.execute_command(b'\x01', b'\x01\x00', b'\x01\x00', b'\x00\x00')
        return response

    def get_input_data_size(self):
        response = self.execute_command(b'\x0e', b'\x74\x00', b'\x01\x00', b'\x02\x00')
        return response

    def get_output_data_size(self):
        response = self.execute_command(b'\x0e', b'\x74\x00', b'\x01\x00', b'\x01\x00')
        return response

    def get_input_data(self):
        response = self.execute_command(b'\x0e', b'\x04\x00', b'\x64\x00', b'\x03\x00')
        return response

    def get_output_data(self):
        response = self.execute_command(b'\x0e', b'\x04\x00', b'\x94\x00', b'\x03\x00')
        return response

    def get_configuration_instance_data(self):
        response = self.execute_command(b'\x0e', b'\x04\x00', b'\xc7\x00', b'\x03\x00')
        return response

    def set_output_data(self, data):
        response = self.execute_command(b'\x10', b'\x04\x00', b'\x94\x00', b'\x03\x00', data=data)
        return response

    def clear_nx_error_status(self):
        response = self.execute_command(b'\x32', b'\x74\x00', b'\x01\x00', b'\x00\x00')
        return response

    def change_nx_state(self, output_watchdog_timeout=100, operational=True):
        if operational:
            data = b'\x08'
        else:
            data = b'\x04'

        data += b'\x00'+int.to_bytes(output_watchdog_timeout, 4, 'little')
        print("data is %s", data)
        response = self.execute_command(b'\x39', b'\x74\x00', b'\x01\x00', b'\x00\x00', data)
        return response

    def read_nx_object(self, unit=0, index=0x1000, sub_index=0, control_field=0):
        data = int.to_bytes(unit, 2, 'little')
        data += int.to_bytes(index, 2, 'little')
        data += int.to_bytes(sub_index, 1, 'little')
        data += int.to_bytes(control_field, 1, 'little')
        response = self.execute_command(b'\x33', b'\x74\x00', b'\x01\x00', b'', data)
        return response
