__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import os
import sys
import tkinter
from tkinter import ttk
from aphyt.omron import n_series
import concurrent.futures
import threading
from signal import signal, SIGINT


class NSeriesThreadDispatcher:
    def __init__(self):
        self.instance = n_series.NSeries()
        self.message_timeout = 0.5
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.futures = []
        self.status_integer = 0
        self.services = None
        self.keep_alive = False

    def start_keep_alive(self, time: float = 0.05):
        if self.instance.connected_cip_dispatcher.is_connected_explicit and self.keep_alive:
            future = self.executor.submit(
                self.instance.connected_cip_dispatcher.list_services, '')
            self.services = future.result()
            delay = threading.Timer(time, self.start_keep_alive)
            delay.start()
            print(self.services)

    def connect_explicit(self, host: str):
        self.instance.connect_explicit(host=host)
        self.instance.register_session()
        self.instance.update_variable_dictionary()
        self.keep_alive = True
        self.start_keep_alive()

    def close_explicit(self):
        self.keep_alive = False
        # self.executor.submit(
        #     self.instance.close_explicit)
        # while self.instance.connected_cip_dispatcher.is_connected_explicit:
        #     pass
        self.executor.shutdown(wait=True)
        if self.instance.connected_cip_dispatcher.is_connected_explicit:
            self.instance.close_explicit()

    def __enter__(self):
        signal(SIGINT, self._sigint_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_explicit()

    def _sigint_handler(self, signal_received, frame):
        print('Ctrl + C handler called')
        self.__exit__(None, None, None)
        sys.exit(0)


class PushButton(tkinter.ttk.Button):
    def __init__(self, master, controller: n_series.NSeries, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._set_value)
        self.bind('<ButtonRelease-1>', self._reset_value)

    def _set_value(self, event):
        self.controller.verified_write_variable(self.variable_name, True)

    def _reset_value(self, event):
        self.controller.verified_write_variable(self.variable_name, False)

