__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


class CIPService:
    pass


class ReadTagService(CIPService):
    def __init__(self):
        self.service_code = b'\x4c'


class WriteTagService(CIPService):
    def __init__(self):
        self.service_code = b'\x4d'


class GetAttributeAll(CIPService):
    def __init__(self):
        self.service_code = b'\x01'


class GetAttributeSingle(CIPService):
    def __init__(self):
        self.service_code = b'\x0e'


class Reset(CIPService):
    def __init__(self):
        self.service_code = b'\x05'


class SetAttributeSingle(CIPService):
    def __init__(self):
        self.service_code = b'\x10'
