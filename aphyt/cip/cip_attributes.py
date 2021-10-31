__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


from aphyt.cip import *


class CIPClass:
    def __init__(self,
                 cip_dispatcher: CIPDispatcher,
                 class_id: bytes,
                 data_type: CIPDataType):
        self.cip_dispatcher = cip_dispatcher
        self.class_id = class_id
        self.data_type = data_type
        self.data_type.data = self.class_id


class CIPInstance:
    def __init__(self,
                 cip_class: CIPClass,
                 instance_id: bytes,
                 data_type: CIPDataType):
        self.cip_class = cip_class
        self.instance_id = instance_id
        self.data_type = data_type
        self.data_type.data = instance_id


class CIPAttribute:
    # ToDo inherit this and use service mixins to describe what it does
    def __init__(self,
                 cip_instance: CIPInstance,
                 attribute_id: bytes,
                 data_type: CIPDataType):
        self.cip_instance: cip_instance
        self.attribute_id = attribute_id
        self.data_type = data_type
        self.data_type.data = attribute_id



