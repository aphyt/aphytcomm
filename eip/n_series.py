__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from eip import *


class NSeriesEIP(EIP):
    def __init__(self):
        super().__init__()

    def get_attribute_all_service(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_all_request = CIPRequest(CIPService.GET_ATTRIBUTE_ALL, tag_route_path)
        return self.execute_cip_command(get_attribute_all_request)

    def get_attribute_single_service(self, tag_route_path):
        # ToDo move up to EIP super class
        get_attribute_single_request = CIPRequest(CIPService.GET_ATTRIBUTE_SINGLE, tag_route_path)
        return self.execute_cip_command(get_attribute_single_request)

    def read_variable(self, variable_name: str):
        route_path = variable_request_path_segment(variable_name)
        response = self.read_tag_service(route_path)
        cip_datatype = self.variables.get(variable_name)
        cip_datatype.from_bytes(response.reply_data)
        return cip_datatype.value()

    def write_variable(self, variable_name: str, data, additional_info: bytes = b''):
        route_path = variable_request_path_segment(variable_name)
        cip_datatype = self.variables.get(variable_name)
        cip_datatype.from_value(data)
        self.write_tag_service(route_path, cip_datatype.data_type_code(), cip_datatype.data)

    def update_variable_dictionary(self):
        """

        :return:
        """
        self._update_data_type_dictionary()
        variable_list = self._get_variable_list()
        attribute_id = 1
        for variable in variable_list:
            route_path = variable_request_path_segment(variable)
            variable_response_bytes = self.read_tag_service(route_path)
            variable_cip_datatype_code = variable_response_bytes.reply_data[0:1]
            variable_cip_datatype_object = self.data_type_dictionary.get(variable_cip_datatype_code)
            if not isinstance(variable_cip_datatype_object, type(None)):
                variable_cip_datatype = variable_cip_datatype_object()
            self.variables.update({variable: variable_cip_datatype})
            if variable[0:1] == '_':
                self.system_variables.update({variable: variable_cip_datatype})
            else:
                self.user_variables.update({variable: variable_cip_datatype})
            attribute_id = attribute_id + 1

    def _update_data_type_dictionary(self):
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
        reply = self.get_attribute_all_service(route_path)
        return int.from_bytes(reply.reply_data[2:4], 'little')
