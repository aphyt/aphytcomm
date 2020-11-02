__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from .cip_datatypes import CIPDataType


class OmronDateAndTime(CIPDataType):
    #     OMRON_DATE_AND_TIME_NSEC = b'\x0a'
    @staticmethod
    def data_type_code():
        return b'\x0a'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronTime(CIPDataType):
    #     OMRON_TIME_NSEC = b'\x09'
    @staticmethod
    def data_type_code():
        return b'\x09'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronTimeOfDay(CIPDataType):
    #     OMRON_TIME_OF_DAY_NSEC = b'\x0b'
    @staticmethod
    def data_type_code():
        return b'\x0b'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronUnion(CIPDataType):
    #     OMRON_UNION = b'\x0c'
    @staticmethod
    def data_type_code():
        return b'\x0c'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronDate(CIPDataType):
    #     OMRON_DATE_NSEC = b'\x08'
    @staticmethod
    def data_type_code():
        return b'\x08'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronEnum(CIPDataType):
    #     OMRON_ENUM = b'\x07'
    @staticmethod
    def data_type_code():
        return b'\x07'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronUnsignedIntegerBCD(CIPDataType):
    #     OMRON_UINT_BCD = b'\x04'  # (1-word unsigned BCD)
    @staticmethod
    def data_type_code():
        return b'\x04'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronUnsignedDoubleInteger(CIPDataType):
    #     OMRON_UDINT_BCD = b'\x05'  # (2-word unsigned BCD)
    @staticmethod
    def data_type_code():
        return b'\x05'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value


class OmronUnsignedLongInteger(CIPDataType):
    #     OMRON_ULINT_BCD = b'\x06'  # (4-word unsigned BCD)
    @staticmethod
    def data_type_code():
        return b'\x06'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value