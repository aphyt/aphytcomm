"""
buttons
~~~~~~~
This module implements various buttons useful for industrial HMIs
"""


import tkinter
from abc import ABC, abstractmethod
from tkinter import ttk

import PIL

from aphyt.omron import NSeriesThreadDispatcher
from aphyt.tkmi.widgets.hmi import HMIPage, MonitoredVariableWidgetMixin


class ImageMultiStateButton(MonitoredVariableWidgetMixin, tkinter.Button):
    def _value_updated(self):
        pass


class ImageButtonMixin(tkinter.Button, ABC):
    def __init__(self, master, scale=1.0, image=None, pressed_image=None, **kwargs):
        self.image = None
        self.pressed_image = None
        if not image:
            # image = tkinter.PhotoImage(width=1, height=1)
            self.image = PIL.Image.open('Transparent_Pixel.png')
        else:
            self.image = PIL.Image.open(image)
        if not pressed_image:
            self.pressed_image = self.image
        else:
            self.pressed_image = PIL.Image.open(pressed_image)
        width = int(scale * float(self.image.size[0]))
        height = int(scale * float(self.image.size[1]))
        self.image = self.image.resize((width, height), PIL.Image.ANTIALIAS)
        self.pressed_image = self.pressed_image.resize((width, height), PIL.Image.ANTIALIAS)
        self.image_tk = PIL.ImageTk.PhotoImage(self.image)
        self.pressed_image_tk = PIL.ImageTk.PhotoImage(self.pressed_image)
        super().__init__(master, image=self.image_tk, compound='center', **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

        @abstractmethod
        def _on_press(self, event):
            pass

        @abstractmethod
        def _on_release(self, event):
            pass


class ImagePageSwitchButton(ImageButtonMixin):
    def __init__(self, master: HMIPage, page: HMIPage, scale=1.0, image=None, pressed_image=None, **kwargs):
        super().__init__(master, image=image, pressed_image=pressed_image, scale=scale, **kwargs)
        self.config(highlightthickness=0, borderwidth=0, activebackground='#4f4f4f')
        self.page = page

    def _on_press(self, event):
        self.config(image=self.pressed_image_tk)

    def _on_release(self, event):
        self.config(image=self.image_tk)
        self.page.tkraise()


class PageSwitchButton(ttk.Button):
    def __init__(self, master: HMIPage, page: HMIPage, **kwargs):
        super().__init__(master, **kwargs)
        self.page = page
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        pass

    def _on_release(self, event):
        self.page.tkraise()


class MomentaryButton(tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._set_value)
        self.bind('<ButtonRelease-1>', self._reset_value)

    def _set_value(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, True)

    def _reset_value(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, False)


class SetButton(tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._set_value)

    def _set_value(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, True)


class ResetButton(tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._reset_value)

    def _reset_value(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, False)


class ToggleButton(tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._toggle_value)

    def _toggle_value(self, event):
        reply = self.dispatcher.read_variable(self.variable_name)
        if reply:
            self.dispatcher.verified_write_variable(self.variable_name, False)
        else:
            self.dispatcher.verified_write_variable(self.variable_name, True)
