__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from ..cip.cip import *
from .eip import *
from abc import ABC, abstractmethod, abstractproperty


class InterfaceConfigurationStatus(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x01', data_type=CIPDoubleWord(), cip_instance=cip_instance)

    @property
    def value(self):
        self.data_type.data = self.get_attribute_single(self.request_path).reply_data
        return self.data_type.value()


class ConfigurationCapability(CIPAttribute, GetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x02', data_type=CIPDoubleWord(),  cip_instance=cip_instance)

    @property
    def value(self):
        self.data_type.data = self.get_attribute_single(self.request_path).reply_data
        print(self.get_attribute_single(self.request_path).bytes)
        return self.data_type.value()


class ConfigurationControl(CIPAttribute, GetAttributeSingleMixin, SetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x03', data_type=CIPDoubleWord(), cip_instance=cip_instance)

    @property
    def value(self):
        self.data_type.data = self.get_attribute_single(self.request_path).reply_data
        return self.data_type.value()

    @value.setter
    def value(self, new_value):
        self.data_type.from_value(new_value)
        self.set_attribute_single(self.request_path, self.data_type.data)


class HostName(CIPAttribute, GetAttributeSingleMixin, SetAttributeSingleMixin):
    def __init__(self, cip_instance: CIPInstance):
        super().__init__(attribute_id=b'\x06', data_type=CIPWord(), cip_instance=cip_instance)

    @property
    def value(self):
        self.data_type.data = self.get_attribute_single(self.request_path).reply_data
        return self.data_type.value()

    @value.setter
    def value(self, new_value):
        self.data_type.from_value(new_value)


class TCPInterfaceObject(CIPClass, GetAttributeSingleMixin):
    def __init__(self,
                 cip_dispatcher: CIPDispatcher):
        super(TCPInterfaceObject, self).__init__(cip_dispatcher, class_id=b'\xf5')
        self.cip_dispatcher = cip_dispatcher
        self.class_id = b'\xf5'
        self.instance_id = b'\x01'
        self.tcp_interface_instance = CIPInstance(self, self.instance_id)
        self.interface_configuration = InterfaceConfigurationStatus(self.tcp_interface_instance)
        self.configuration_capability = ConfigurationCapability(self.tcp_interface_instance)
        self.configuration_control = ConfigurationControl(self.tcp_interface_instance)
        self.host_name = HostName(self.tcp_interface_instance)


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
