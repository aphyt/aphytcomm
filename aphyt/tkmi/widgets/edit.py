import struct
import tkinter
from tkinter import ttk, messagebox
from aphyt.omron import NSeriesThreadDispatcher


class DataEdit(ttk.Entry):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.current_string = None
        self.type = None
        self._get_data()
        self.delay = None
        self.dispatcher.connection_status.bind_to_session_status(self._get_data)
        self.validate_command = (self.register(self.validate_entry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.config(validate='focus', validatecommand=self.validate_command)
        self.bind("<Return>", (lambda event: self._enter_function()))

    def _get_data(self):
        if self.dispatcher.connection_status.has_session:
            data = self.dispatcher.read_variable(self.variable_name)
            self.current_string = str(data)
            self.type = type(data)
            self.delete(0, 'end')
            self.insert(0, self.current_string)

    def _enter_function(self):
        # print(f'Enter pressed in {self.variable_name}')
        if self.validate():
            self.current_string = self.get()
        else:
            self.delete(0, 'end')
            self.insert(0, self.current_string)
            tkinter.messagebox.showerror('Write Error', 'Could not write value. Is it the correct type?')

    def validate_entry(self, d, i, P, s, S, v, V, W):
        success = False
        try:
            value = self.type(self.get())
            self.dispatcher.verified_write_variable(self.variable_name, value)
            success = True
        except struct.error as error:
            success = False
        except ValueError as error:
            success = False
        return success
