__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from ..cip import *
from .eip import *
from abc import ABC, abstractmethod, abstractproperty


class CIPObject(ABC):
    @abstractmethod
    def __init__(self, dispatcher: EIPConnectedCIPDispatcher):
        """Docstring to pass"""

    @abstractmethod
    def from_bytes(self):
        """Docstring to pass"""


class InstanceAttribute:
    def __init__(self,
                 instance_attribute_id: bytes,
                 data_type: CIPDataType,
                 writeable: bool):
        self.instance_attribute_id = instance_attribute_id
        self.data_type = data_type
        self.writeable = writeable


class InterfaceConfigurationStatus(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self,
                 cip_dispatcher: CIPDispatcher):
        super().__init__(cip_dispatcher, attribute_id=b'\x01', data_type=CIPDoubleWord())


class TCPInterfaceObject2(CIPObject):
    def __init__(self, cip_dispatcher: EIPConnectedCIPDispatcher):
        self.cip_dispatcher = cip_dispatcher
        self.class_id = b'\xf5'
        self.instance_id = b'\x01'

    def from_bytes(self):
        pass


class TCPInterfaceObject(CIPObject):
    def __init__(self, dispatcher: EIPConnectedCIPDispatcher):
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
