__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from ..eip import *


class TCPInterfaceObject(CIPObject, GetAttributeSingleMixin, SetAttributeSingleMixin, GetAttributeAllMixin):
    def __init__(self, cip_dispatcher: EIPConnectedCIPDispatcher):
        super().__init__(b'\xf5')
        self.instance_id = b'\x01'
        self.cip_dispatcher = cip_dispatcher
        self.revision = CIPAttribute(class_id=self.class_id, instance_id=b'\x00',
                                     attribute_id=b'\x01', data_type=CIPUnsignedInteger())
        self.interface_configuration_status = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                           attribute_id=b'\x01', data_type=CIPDoubleWord())
        self.configuration_capability = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                     attribute_id=b'\x02', data_type=CIPDoubleWord())
        self.configuration_control = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                  attribute_id=b'\x03', data_type=CIPDoubleWord(), writeable=True)
        physical_link_object_structure = CIPStructure()
        physical_link_object_structure.variable_name = "Physical Link Object"
        physical_link_object_structure.add_member('Path Size', CIPUnsignedInteger())
        # This is a hack! I don't anything about an EPATH type, but it's four bytes with an alignment of 1
        physical_link_object_structure.add_member('Path1', CIPByte())
        physical_link_object_structure.add_member('Path2', CIPByte())
        physical_link_object_structure.add_member('Path3', CIPByte())
        physical_link_object_structure.add_member('Path4', CIPByte())
        self.physical_link_object = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                 attribute_id=b'\x04', data_type=physical_link_object_structure)
        interface_configuration = CIPStructure()
        interface_configuration.variable_name = "Interface Configuration"
        interface_configuration.add_member('IP Address', CIPUnsignedDoubleInteger())
        interface_configuration.add_member('Subnet Mask', CIPUnsignedDoubleInteger())
        interface_configuration.add_member('Default Gateway', CIPUnsignedDoubleInteger())
        interface_configuration.add_member('Primary Nameserver', CIPUnsignedDoubleInteger())
        interface_configuration.add_member('Secondary Nameserver', CIPUnsignedDoubleInteger())
        interface_configuration.add_member('Domain Name', CIPWord())
        self.interface_configuration = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                    attribute_id=b'\x05', data_type=interface_configuration,
                                                    writeable=True)
        self.host_name = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                      attribute_id=b'\x06', data_type=CIPDoubleWord(), writeable=True)
        self.encapsulation_inactivity_timeout = CIPAttribute(class_id=self.class_id, instance_id=b'\x01',
                                                             attribute_id=b'\x0d', data_type=CIPDoubleWord(),
                                                             writeable=True)

    def get_attribute_all(self):
        request_path = address_request_path_segment(class_id=self.class_id, instance_id=self.instance_id)
        reply = self.get_attribute_all_from_path(request_path)
        return reply
