__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from .cip import *
from .cip_attributes import *
from .cip_datatypes import *


class CIPService:
    """
    ToDo eventually all services should be mixins and then the cip dispatcher will not contain the
    reading, writing, getting, setting and resetting methods
    """
    READ_TAG_SERVICE = b'\x4c'
    READ_TAG_FRAGMENTED_SERVICE = b'\x52'
    WRITE_TAG_SERVICE = b'\x4d'
    WRITE_TAG_FRAGMENTED_SERVICE = b'\x53'
    READ_MODIFY_WRITE_TAG_SERVICE = b'\x4e'
    # w506_nx_nj - series_cpu_unit_built - in_ethernet_ip_port_users_manual_en.pdf
    # 303 of 570 CIP Object Services
    GET_ATTRIBUTE_ALL = b'\x01'
    GET_ATTRIBUTE_SINGLE = b'\x0e'
    RESET = b'\x05'
    SET_ATTRIBUTE_SINGLE = b'\x10'

    def __init__(self, cip_dispatcher: CIPDispatcher, **kwargs):
        self.cip_dispatcher = cip_dispatcher


class ReadTagServiceMixin(CIPService):
    def __init__(self, cip_dispatcher: CIPDispatcher):
        super().__init__(cip_dispatcher)

    def read_tag(self, tag_request_path, number_of_elements=1) -> CIPReply:
        service_code = b'\x4c'
        read_tag_request = \
            CIPRequest(service_code, tag_request_path, number_of_elements.to_bytes(2, 'little'))
        return self.cip_dispatcher.execute_cip_command(read_tag_request)


class WriteTagServiceMixin(CIPService):
    def __init__(self, cip_dispatcher: CIPDispatcher):
        super().__init__(cip_dispatcher)

    def write_tag(self, tag_request_path, request_service_data: CIPCommonFormat, number_of_elements=1):
        service_code = b'\x4d'
        data = request_service_data.data_type + \
            int(request_service_data.additional_info_length).to_bytes(1, 'little') + \
            request_service_data.additional_info + number_of_elements.to_bytes(2, 'little') + \
            request_service_data.data
        write_tag_request = CIPRequest(service_code, tag_request_path, data)
        return self.cip_dispatcher.execute_cip_command(write_tag_request)


class GetAttributeAllMixin(CIPService):
    def __init__(self, cip_dispatcher: CIPDispatcher):
        super().__init__(cip_dispatcher)

    def get_attribute_all_from_path(self, tag_request_path):
        service_code = b'\x01'
        get_attribute_all_request = CIPRequest(service_code, tag_request_path)
        return self.cip_dispatcher.execute_cip_command(get_attribute_all_request)

    # def get_attribute_all(self, cip_attribute: CIPAttribute) -> bytes:
    #     reply = self.get_attribute_all_from_path(cip_attribute.request_path)
    #     return reply.reply_data


class GetAttributeSingleMixin(CIPService):
    """Always use the Set mixins before the get mixins so that """
    def __init__(self, cip_dispatcher: CIPDispatcher, **kwargs):
        super().__init__(cip_dispatcher, **kwargs)

    def get_attribute_single_from_path(self, tag_request_path) -> CIPReply:
        service_code = b'\x0e'
        get_attribute_single_request = \
            CIPRequest(service_code, tag_request_path)
        return self.cip_dispatcher.execute_cip_command(get_attribute_single_request)

    def get_attribute_single(self, cip_attribute: CIPAttribute) -> CIPAttribute:
        reply = self.get_attribute_single_from_path(cip_attribute.request_path)
        cip_attribute.data_type.data = reply.reply_data
        return cip_attribute


class SetAttributeSingleMixin(CIPService):
    def __init__(self, cip_dispatcher: CIPDispatcher, **kwargs):
        super().__init__(cip_dispatcher, **kwargs)

    def set_attribute_single_from_path(self, tag_request_path, data: bytes):
        service_code = b'\x10'
        set_attribute_single_request = CIPRequest(service_code, tag_request_path, data)
        return self.cip_dispatcher.execute_cip_command(set_attribute_single_request)

    def set_attribute_single(self, cip_attribute: CIPAttribute):
        assert (cip_attribute.writeable is True)
        self.set_attribute_single_from_path(cip_attribute.request_path, data=cip_attribute.data_type.data)


class ResetMixin(CIPService):
    def __init__(self, cip_dispatcher: CIPDispatcher):
        super().__init__(cip_dispatcher)

    def reset(self, tag_request_path):
        service_code = b'\x05'
        reset_request = CIPRequest(service_code, tag_request_path)
        return self.cip_dispatcher.execute_cip_command(reset_request)
