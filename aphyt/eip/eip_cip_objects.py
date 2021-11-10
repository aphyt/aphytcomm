__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.cip import *
from .eip import *
from abc import ABC, abstractmethod, abstractproperty


class InterfaceConfigurationStatus(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x01', data_type=CIPDoubleWord(), cip_instance=cip_instance)


class ConfigurationCapability(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x02', data_type=CIPDoubleWord(), cip_instance=cip_instance)


class ConfigurationControl(CIPAttribute, SetAttributeSingleMixin, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x03', data_type=CIPDoubleWord(), cip_instance=cip_instance)


class PhysicalLinkObject(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x04', data_type=CIPStructure(), cip_instance=cip_instance)
        self.data_type.variable_name = "Physical Link Object"
        self.data_type.add_member('Path Size', CIPUnsignedInteger())
        self.data_type.add_member('Path', CIPUnsignedDoubleInteger())


class InterfaceConfiguration(CIPAttribute, SetAttributeSingleMixin, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x05', data_type=CIPStructure(), cip_instance=cip_instance)
        self.data_type.variable_name = "Interface Configuration"
        self.data_type.add_member('IP Address', CIPUnsignedDoubleInteger())
        self.data_type.add_member('Subnet Mask', CIPUnsignedDoubleInteger())
        self.data_type.add_member('Default Gateway', CIPUnsignedDoubleInteger())
        self.data_type.add_member('Primary Nameserver', CIPUnsignedDoubleInteger())
        self.data_type.add_member('Secondary Nameserver', CIPUnsignedDoubleInteger())


class HostName(CIPAttribute, SetAttributeSingleMixin, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x06', data_type=CIPWord(), cip_instance=cip_instance)


class EncapsulationInactivityTimeout(CIPAttribute, SetAttributeSingleMixin, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x0d', data_type=CIPUnsignedInteger(), cip_instance=cip_instance)


class Revision(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x01', data_type=CIPUnsignedInteger(), cip_instance=cip_instance)


class TCPInterfaceObject(CIPClass, GetAttributeSingleMixin):
    def __init__(self,
                 cip_dispatcher: CIPDispatcher):
        super(TCPInterfaceObject, self).__init__(cip_dispatcher, class_id=b'\xf5')
        self.cip_dispatcher = cip_dispatcher
        self.class_id = b'\xf5'
        self.instance_id = b'\x01'
        self.tcp_interface_instance = CIPInstance(self, self.instance_id)
        self.tcp_class_instance = CIPInstance(self, b'\x00')
        self.revision = Revision(self.tcp_class_instance)
        self.interface_configuration_status = InterfaceConfigurationStatus(self.tcp_interface_instance)
        self.configuration_capability = ConfigurationCapability(self.tcp_interface_instance)
        self.configuration_control = ConfigurationControl(self.tcp_interface_instance)
        self.physical_link_object = PhysicalLinkObject(self.tcp_interface_instance)
        self.interface_configuration = InterfaceConfiguration(self.tcp_interface_instance)
        self.host_name = HostName(self.tcp_interface_instance)
        self.encapsulation_inactivity_timeout = EncapsulationInactivityTimeout(self.tcp_interface_instance)


#
# class TCPInterfaceObject(CIPObject):
#     def __init__(self, dispatcher: EIPConnectedCIPDispatcher):
#         self.dispatcher = dispatcher
#         self.class_id = b'\xf5'
#         self.instance_id = b'\x01'
#         self.interface_configuration_status = InstanceAttribute(b'\x01', CIPDoubleWord(), False)
#         self.configuration_capability = InstanceAttribute(b'\x02', CIPDoubleWord(), False)
#         self.configuration_control = InstanceAttribute(b'\x03', CIPDoubleWord(), True)
#         self.physical_link_object = CIPStructure()
#         self.physical_link_object.add_member('path size', CIPUnsignedInteger())
#         self.physical_link_object.add_member('path', CIPUnsignedDoubleInteger())
#         self.physical_link_object = InstanceAttribute(b'\x04', self.physical_link_object, True)
#         self.interface_configuration = CIPStructure()
#         self.interface_configuration.add_member('IP Address', CIPUnsignedDoubleInteger())
#         self.interface_configuration.add_member('Subnet Mask', CIPUnsignedDoubleInteger())
#         self.interface_configuration.add_member('Default Gateway', CIPUnsignedDoubleInteger())
#         self.interface_configuration.add_member('Primary Nameserver', CIPUnsignedDoubleInteger())
#         self.interface_configuration.add_member('Secondary Nameserver', CIPUnsignedDoubleInteger())
#         self.interface_configuration.add_member('Domain Name', CIPUnsignedInteger())
#         self.interface_configuration = InstanceAttribute(b'\x05', self.interface_configuration, True)
#         self.hostname = InstanceAttribute(b'\x06', CIPUnsignedInteger(), True)
#         self.encapsulation_inactivity_timeout = InstanceAttribute(b'\x0d', CIPUnsignedInteger(), True)
#
#     def from_bytes(self):
#         pass
