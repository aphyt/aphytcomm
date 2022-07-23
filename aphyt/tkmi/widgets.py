__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import os
import socket
import sys
import time
import tkinter
from tkinter import ttk
from aphyt.omron import n_series
import concurrent.futures
import threading
from signal import signal, SIGINT


class NSeriesThreadDispatcher:
    def __init__(self):
        self._instance = n_series.NSeries()
        self._host = None
        self.message_timeout = 0.5
        self.executor = None
        self.futures = []
        self.status_integer = 0
        self.services = None
        self.keep_alive = False
        self.has_session = False

    def _execute_eip_command(self, command, *args, **kwargs):
        future = self.executor.submit(command, *args, **kwargs)
        try:
            result = future.result()
            return result
        except socket.error as exception:
            print(exception)
            self._reconnect()

    def _reconnect(self):
        temp_keep_alive = self.keep_alive
        self.keep_alive = False
        try:
            self.close_explicit()
        except Exception as error:
            print(error)
        self.connect_explicit(self._host)
        if self.has_session:
            self.register_session()
        self.keep_alive = temp_keep_alive
        if self.keep_alive:
            self.start_keep_alive()

    def start_keep_alive(self, keep_alive_time: float = 0.05):
        if self._instance.connected_cip_dispatcher.is_connected_explicit and self.keep_alive:
            self.services = self._execute_eip_command(self._instance.connected_cip_dispatcher.list_services, '')
            delay = threading.Timer(keep_alive_time, self.start_keep_alive)
            delay.start()

    def connect_explicit(self, host: str, reconnect_time: float = 1.0):
        connected = False
        while not connected:
            self._host = host
            try:
                self._instance.connect_explicit(host=self._host)
                self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                connected = True
            except socket.error as err:
                print(f"Failed to connect, trying again in {reconnect_time} seconds")
                time.sleep(reconnect_time)

    def register_session(self):
        self._instance.register_session()
        self.has_session = True

    def update_variable_dictionary(self):
        self._instance.update_variable_dictionary()

    def save_current_dictionary(self, file_name: str):
        self._instance.save_current_dictionary(file_name)

    def load_dictionary_file(self, file_name: str):
        self._instance.load_dictionary_file(file_name)

    def read_variable(self, variable_name: str):
        return self._execute_eip_command(self._instance.read_variable, variable_name)

    def write_variable(self, variable_name: str, data):
        return self._execute_eip_command(self._instance.write_variable, variable_name, data)

    def verified_write_variable(self, variable_name: str, data):
        return self._execute_eip_command(self._instance.verified_write_variable, variable_name, data)

    def close_explicit(self):
        self.executor.shutdown()
        if self._instance.connected_cip_dispatcher.is_connected_explicit:
            self._instance.close_explicit()

    def __enter__(self):
        signal(SIGINT, self._sigint_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_explicit()

    def _sigint_handler(self, signal_received, frame):
        print('Program interrupted with Ctrl+C')
        self.__exit__(None, None, None)
        sys.exit(0)


class DataDisplay(tkinter.ttk.Label):
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self._update_data()
        self.delay = None

    def _update_data(self):
        if self.controller._instance.connected_cip_dispatcher.is_connected_explicit:
            data = str(self.controller.read_variable(self.variable_name))
            self.config(text=data)
            self.delay = threading.Timer(0.1, self._update_data)
            self.delay.start()


class PushButton(tkinter.ttk.Button):
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._set_value)
        self.bind('<ButtonRelease-1>', self._reset_value)

    def _set_value(self, event):
        self.controller.verified_write_variable(self.variable_name, True)

    def _reset_value(self, event):
        self.controller.verified_write_variable(self.variable_name, False)


class SetButton(tkinter.ttk.Button):
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._set_value)

    def _set_value(self, event):
        self.controller.verified_write_variable(self.variable_name, True)


class ResetButton(tkinter.ttk.Button):
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._reset_value)

    def _reset_value(self, event):
        self.controller.verified_write_variable(self.variable_name, False)

