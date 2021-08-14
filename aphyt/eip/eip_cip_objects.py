__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.cip import *
from .eip import *


class InstanceAttribute:
    def __init__(self,
                 instance_attribute_id: bytes,
                 data_type: CIPDataType,
                 writeable: bool):
        self.instance_attribute_id = instance_attribute_id
        self.data_type = data_type
        self.writeable = writeable


class TCPInterfaceObject:
    def __init__(self, dispatcher: EIP):
        super().__init__()
        self.dispatcher = dispatcher
        self.class_id = b'\xf5'
        self.instance_id = b'\x01'
        self.interface_configuration_status = InstanceAttribute(b'\x01', CIPDoubleWord(), False)
        self.configuration_capability = InstanceAttribute(b'\x02', CIPDoubleWord(), False)
        self.configuration_control = InstanceAttribute(b'\x03', CIPDoubleWord(), True)
        self.physical_link_object = CIPStructure()
        self.physical_link_object.add_member('path size', CIPUnsignedInteger())
        self.physical_link_object.add_member('path', CIPUnsignedDoubleInteger())
        self.physical_link_object = InstanceAttribute(b'\x04', self.physical_link_object, True)
        self.interface_configuration = CIPStructure()
        self.interface_configuration.add_member('IP Address', CIPUnsignedDoubleInteger())
        self.interface_configuration.add_member('Subnet Mask', CIPUnsignedDoubleInteger())
        self.interface_configuration.add_member('Default Gateway', CIPUnsignedDoubleInteger())
        self.interface_configuration.add_member('Primary Nameserver', CIPUnsignedDoubleInteger())
        self.interface_configuration.add_member('Secondary Nameserver', CIPUnsignedDoubleInteger())
        self.interface_configuration.add_member('Domain Name', CIPUnsignedInteger())
        self.interface_configuration = InstanceAttribute(b'\x05', self.interface_configuration, True)
        self.hostname = InstanceAttribute(b'\x06', CIPUnsignedInteger(), True)
        self.encapsulation_inactivity_timeout = InstanceAttribute(b'\x0d', CIPUnsignedInteger(), True)

    def from_bytes(self):
        pass
