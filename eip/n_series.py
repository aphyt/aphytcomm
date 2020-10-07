from eip import *


class NSeriesEIP(EIP2):
    def __init__(self):
        super().__init__()

    def get_attribute_all_service(self, tag_route_path):
        get_attribute_all_request = CIPRequest(CIPService.GET_ATTRIBUTE_ALL, tag_route_path)
        return self.execute_cip_command(get_attribute_all_request)

    def get_attribute_single(self, tag_route_path):
        get_attribute_single_request = CIPRequest(CIPService.GET_ATTRIBUTE_SINGLE, tag_route_path)
        return self.execute_cip_command(get_attribute_single_request)

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
