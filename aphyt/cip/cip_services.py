__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


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


class ReadTagServiceMixin(CIPService):
    def __init__(self):
        self.service_code = CIPService.READ_TAG_SERVICE


class WriteTagServiceMixin(CIPService):
    def __init__(self):
        self.service_code = b'\x4d'


class GetAttributeAllMixin(CIPService):
    def __init__(self):
        self.service_code = b'\x01'


class GetAttributeSingleMixin(CIPService):
    def __init__(self):
        self.service_code = b'\x0e'


class SetAttributeSingleMixin(CIPService):
    def __init__(self):
        self.service_code = b'\x10'


class ResetMixin(CIPService):
    def __init__(self):
        self.service_code = b'\x05'
