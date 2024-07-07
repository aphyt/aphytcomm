__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import nseries_fixtures
from aphyt import omron


class TestOnline(nseries_fixtures.BaseNSeries):

    # def __init__(self):
    eip_instance = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.eip_instance = omron.n_series.NSeriesThreadDispatcher()
        cls.eip_instance.connect_explicit('192.168.250.9')
        cls.eip_instance.register_session()
        # cls.eip_instance.update_variable_dictionary()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.eip_instance.close_explicit()

