__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import tkinter
from tkinter import ttk
from aphyt.omron import NSeriesThreadDispatcher

DEFAULT_PADDING = 5

class HMIPage(tkinter.ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=0, column=0, sticky="nsew")


class HMIWidgetFrame(tkinter.ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def add_widget(self, widget: tkinter.ttk.Widget, vertical=True):
        if vertical:
            widget.grid(row=self.grid_size()[1], padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        else:
            widget.grid(column=self.grid_size()[0] + 1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)


class PageSwitchButton(ttk.Button):
    def __init__(self, master: HMIPage, page: HMIPage, **kwargs):
        super().__init__(master, **kwargs)
        self.page = page
        self.bind('<ButtonPress-1>', self._on_press)

    def _on_press(self, event):
        self.page.tkraise()


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


class ToggleButton(tkinter.ttk.Button):
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._toggle_value)

    def _toggle_value(self, event):
        reply = self.controller.read_variable(self.variable_name)
        if reply:
            self.controller.verified_write_variable(self.variable_name, False)
        else:
            self.controller.verified_write_variable(self.variable_name, True)
