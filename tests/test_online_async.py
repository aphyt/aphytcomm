__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import asyncio

import nseries_fixtures
from aphyt import omron




class AsyncTestOnline(nseries_fixtures.AsyncBaseNSeries):

    # def __init__(self):
    eip_instance = None

    @classmethod
    def setUpClass(cls) -> None:
        # Handling asynchronous set up
        cls.loop = asyncio.new_event_loop()  # create and set new event loop
        asyncio.set_event_loop(cls.loop)
        cls.loop.run_until_complete(cls.asyncSetUpClass())

    @classmethod
    async def asyncSetUpClass(cls):
        # assign measurement object to unit test object
        cls.eip_instance = omron.n_series.AsyncNSeries()
        await cls.eip_instance.connect_explicit('192.168.250.9')
        await cls.eip_instance.register_session()

    @classmethod
    async def tearDownClass(cls) -> None:
        await cls.eip_instance.close_explicit()
        if cls.loop.is_running():
            cls.loop.stop()
        cls.loop.close()

