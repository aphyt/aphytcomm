__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


from aphyt.cip.cip_datatypes import *
from aphyt.cip.cip import *


class CIPObject:
    def __init__(self, class_id: bytes, **kwargs):
        self.class_id = class_id


class CIPAttribute:
    def __init__(self,
                 class_id: bytes,
                 instance_id: bytes,
                 attribute_id: bytes,
                 data_type: CIPDataType,
                 writeable: bool = False):
        self.class_id = class_id
        self.instance_id = instance_id
        self.attribute_id = attribute_id
        self.data_type = data_type
        self.writeable = writeable
        self.request_path = address_request_path_segment(self.class_id,
                                                         self.instance_id,
                                                         self.attribute_id)

    def __repr__(self):
        return str(self.data_type.value())
