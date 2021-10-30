__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.cip import *


class TCPIPInterfaceObject:
    """
    class id, instance id, class attribute id, instance attribute id
    writable?
    data type and default value
    Should CIP objects have a dependency injection that allows easy reading and writing of attributes?
    """
    class_id = b'\xf5'

    def __init__(self):
        pass
