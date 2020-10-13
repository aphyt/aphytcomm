__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from .cip_datatypes import CIPDataType


class OmronDateAndTime(CIPDataType):
    @staticmethod
    def data_type_code():
        return b'\x0a'  #

    def value(self):
        return self.data

    def from_value(self, value):
        self.data = value
