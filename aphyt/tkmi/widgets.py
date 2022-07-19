__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import os
import tkinter
from tkinter import ttk
from aphyt.omron import n_series


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

