from eip import *


class NSeriesEIP(EIP2):
    def __init__(self):
        super().__init__()

    def get_attribute_all_service(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_all_request = CIPRequest(CIPService.GET_ATTRIBUTE_ALL, tag_route_path)
        return self.execute_cip_command(get_attribute_all_request)

    def get_attribute_single(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_single_request = CIPRequest(CIPService.GET_ATTRIBUTE_SINGLE, tag_route_path)
        return self.execute_cip_command(get_attribute_single_request)

    def read_variable(self, variable_name: str):
        # ToDo make a reply to rational response based on data type in response
        route_path = variable_request_path_segment(variable_name)
        read_variable_request = CIPRequest(CIPService.READ_TAG_SERVICE, route_path, b'\x01\x00')
        return self.execute_cip_command(read_variable_request).reply_data

    def write_variable(self, variable_name: str, data, additional_info: bytes = b''):
        pass

    def update_variable_dictionary(self):
        """

        :return:
        """
        variable_list = self._get_variable_list()
        attribute_id = 1
        for variable in variable_list:
            # variable_response_bytes = self._get_variable_with_cip_data_type(variable)
            variable_response_bytes = self.read_variable(variable)
            self.variables.update({variable: variable_response_bytes.data_type_code})
            if variable[0:1] == '_':
                self.system_variables.update({variable: variable_response_bytes.data_type_code})
            else:
                self.user_variables.update({variable: variable_response_bytes.data_type_code})
            attribute_id = attribute_id + 1

    def update_data_type_dictionary(self):
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
        # reply = self._get_request_route_path(route_path)
        reply = self.get_attribute_all_service(route_path)
        #return int.from_bytes(reply.bytes[10:12], 'little')
        return int.from_bytes(reply.reply_data[2:4], 'little')
