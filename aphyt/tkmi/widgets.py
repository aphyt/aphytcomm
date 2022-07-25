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


class EIPConnectionStatus:
    def __init__(self):
        self.connected = False
        self.connecting = False
        self.reconnecting = False
        self._has_session = False
        self.persist_session = False
        self._session_status_observers = []
        self.keep_alive = False
        self.keep_alive_running = False

    def bind_to_session_status(self, callback):
        """
        Observer Pattern: Allow widgets to bind a callback function that will act on reestablished session
        :param callback:
        :return:
        """
        self._session_status_observers.append(callback)

    @property
    def has_session(self):
        return self._has_session

    @has_session.setter
    def has_session(self, value):
        self._has_session = value
        for callback in self._session_status_observers:
            print(f'announcing change: has_session is {self._has_session}')
            callback()


class NSeriesThreadDispatcher:
    def __init__(self):
        self._instance = n_series.NSeries()
        self._host = None
        self.message_timeout = 0.5
        self.executor = None
        self.futures = []
        self.status_integer = 0
        self.services = None
        self.connection_status = EIPConnectionStatus()

    def _execute_eip_command(self, command, *args, **kwargs):
        if self.connection_status.connected:
            future = self.executor.submit(command, *args, **kwargs)
            try:
                result = future.result()
                return result
            except socket.error as err:
                print(f'{err} occurred in _execute_eip_command')
                self.connection_status.connected = False
                self.connection_status.keep_alive_running = False
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

    def _reconnect(self, already_executing=False):
        if not already_executing and not self.connection_status.reconnecting:
            self.connection_status.reconnecting = True
            self._reconnect(already_executing=True)
        elif self.connection_status.reconnecting and already_executing:
            if not self.connection_status.connected:
                try:
                    self.close_explicit()
                except Exception as err:
                    print(f'{err} occurred in close_explicit')
                self.connect_explicit(self._host)
                self._reconnect(already_executing=True)
            if (self.connection_status.persist_session
                    and self.connection_status.connected
                    and not self.connection_status.has_session):
                self.register_session()
                self._reconnect(already_executing=True)
            elif not self.connection_status.persist_session and not self.connection_status.keep_alive:
                self.connection_status.reconnecting = False
            if self.connection_status.keep_alive and self.connection_status.has_session:
                self.start_keep_alive()
            elif not self.connection_status.keep_alive:
                self.connection_status.reconnecting = False

    def start_keep_alive(self, keep_alive_time: float = 0.05):
        self.connection_status.keep_alive = True
        if (self.connection_status.connected
                and self.connection_status.keep_alive
                and self.connection_status.has_session):
            self.connection_status._keep_alive_running = True
            self.services = self._execute_eip_command(self._instance.connected_cip_dispatcher.list_services, '')
            print(self.services)
            delay = threading.Timer(keep_alive_time, self.start_keep_alive, [keep_alive_time])
            delay.start()

    def connect_explicit(self, host: str, retry_time: float = 1.0):
        self.connection_status.connecting = True
        if not self.connection_status.connected:
            self._host = host
            try:
                self._instance.connect_explicit(host=self._host)
                self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                self.connection_status.connected = self._instance.connected_cip_dispatcher.is_connected_explicit
                self.connection_status.connecting = False
            except socket.error as err:
                print(f"Failed to connect, trying again in {retry_time} seconds")
                delay = threading.Timer(retry_time, self.connect_explicit, [host, retry_time])
                delay.start()

    def register_session(self, retry_time: float = 1.0):
        reply = self._instance.register_session()
        session_id = self._instance.connected_cip_dispatcher.session_handle_id
        print(f'reply is {reply}')
        print(session_id)
        if session_id != b'\x00\x00\x00\x00\x00\x00\x00\x00':
            self.connection_status.has_session = True
        else:
            print(f"Failed to register session, trying again in {retry_time} seconds")
            delay = threading.Timer(retry_time, self.register_session, [retry_time])
            delay.start()
        self.connection_status.persist_session = True
        return reply

    def unregister_session(self):
        self.connection_status.has_session = False
        self.connection_status.persist_session = False

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
        self.connection_status.connected = False
        self.connection_status.has_session = False
        self.connection_status._keep_alive_running = False
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
        self.controller.connection_status.bind_to_session_status(self._update_data)

    def _update_data(self):
        if self.controller.connection_status.has_session:
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

