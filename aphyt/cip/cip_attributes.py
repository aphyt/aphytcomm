__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


from ..cip import *


class CIPAttribute:
    def __init__(self, cip_dispatcher: CIPDispatcher):
        self.cip_dispatcher = cip_dispatcher
        self.attribute_id = None
        self.attribute = None  # CIPDataType
