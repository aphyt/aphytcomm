__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import os
import socket
import struct
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
        self._observers = []
        self.status_integer = 0
        self.services = None
        self.connected = False
        self.reconnecting = False
        self.keep_alive = False
        self._has_session = False
        self._persist_session = False

    def bind_to_session_status(self, callback):
        """
        Observer Pattern: Allow widgets to bind a callback function that will act on reestablished session
        :param callback:
        :return:
        """
        self._observers.append(callback)

    @property
    def has_session(self):
        return self._has_session

    @has_session.setter
    def has_session(self, value):
        self._has_session = value
        for callback in self._observers:
            print(f'announcing change: has_session is {self._has_session}')
            callback()

    def _execute_eip_command(self, command, *args, **kwargs):
        if self.connected:
            future = self.executor.submit(command, *args, **kwargs)
            try:
                result = future.result()
                return result
            except socket.error as err:
                print(f'{err} occurred in _execute_eip_command')
                self.connected = False
                self.executor.shutdown()
                self._reconnect()
        else:
            self._reconnect()

    def retry_command(self, command, retry_time: float = 0.05, *args, **kwargs):
        reply = command(*args, **kwargs)
        if not reply:
            delay = threading.Timer(retry_time, self.retry_command, command,
                                    *args, **dict(**kwargs, retry_time=retry_time))
            delay.start()
        return reply

    def _reconnect(self):
        if not self.reconnecting and not self.connected:
            self.reconnecting = True
            # ToDo Figure out how to separate keeping alive from ideal state
            temp_keep_alive = self.keep_alive
            self.keep_alive = False
            try:
                self.close_explicit()
            except Exception as err:
                print(f'{err} occurred in close_explicit')
            self.connect_explicit(self._host)
            reply = b''
            while reply == b'':
                reply = self._instance.connected_cip_dispatcher.list_services()
                print(f'I\'m trying to list services {reply}')
                time.sleep(1)
            if self._persist_session:
                reply = b'\x00\x00\x00\x00\x00\x00\x00\x00'
                while reply == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                    print(f"In persist while at {time.time()}")
                    reply = self.register_session()
                    print(f'registered reply is: {reply}')
                    time.sleep(0.1)
                print('WE DID IT!')
            self.keep_alive = temp_keep_alive
            if self.keep_alive:
                self.start_keep_alive()
            self.reconnecting = False

    def start_keep_alive(self, keep_alive_time: float = 0.05):
        self.keep_alive = True
        if self.connected and self.keep_alive:
            self.services = self._execute_eip_command(self._instance.connected_cip_dispatcher.list_services, '')
            delay = threading.Timer(keep_alive_time, self.start_keep_alive)
            delay.start()

    def connect_explicit(self, host: str, reconnect_time: float = 1.0):
        self.connected = False
        while not self.connected:
            self._host = host
            try:
                self._instance.connect_explicit(host=self._host)
                self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                self.connected = self._instance.connected_cip_dispatcher.is_connected_explicit
            except socket.error as err:
                print(f"Failed to connect, trying again in {reconnect_time} seconds")
                time.sleep(reconnect_time)

    def register_session(self):
        reply = self._instance.register_session()
        session_id = self._instance.connected_cip_dispatcher.session_handle_id
        print(f'reply is {reply}')
        print(session_id)
        if session_id != b'\x00\x00\x00\x00\x00\x00\x00\x00':
            self.has_session = True
        self._persist_session = True
        return reply

    def unregister_session(self):
        self.has_session = False
        self._persist_session = False

    def update_variable_dictionary(self):
        self._instance.update_variable_dictionary()

    def save_current_dictionary(self, file_name: str):
        self._instance.save_current_dictionary(file_name)

    def load_dictionary_file(self, file_name: str):
        self._instance.load_dictionary_file(file_name)

    def read_variable(self, variable_name: str):
        try:
            return self._execute_eip_command(self._instance.read_variable, variable_name)
        except struct.error as err:
            pass

    def write_variable(self, variable_name: str, data):
        return self._execute_eip_command(self._instance.write_variable, variable_name, data)

    def verified_write_variable(self, variable_name: str, data):
        try:
            return self._execute_eip_command(self._instance.verified_write_variable, variable_name, data)
        except struct.error as err:
            pass

    def close_explicit(self):
        self.connected = False
        self.has_session = False
        self.executor.shutdown(wait=True)
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
        self.controller.bind_to_session_status(self._update_data)

    def _update_data(self):
        if self.controller.has_session:
            data = str(self.controller.read_variable(self.variable_name))
            self.config(text=data)
            self.after(100, self._update_data)
            # self.delay = threading.Timer(0.1, self._update_data)
            # self.delay.start()


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

