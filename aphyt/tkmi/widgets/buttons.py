"""
buttons
~~~~~~~
This module implements various buttons useful for industrial HMIs
"""


import tkinter
from abc import ABC, abstractmethod
from tkinter import ttk, messagebox
from typing import Dict, Union
import logging

import PIL
from PIL import Image, ImageTk

from aphyt.omron import NSeriesThreadDispatcher
from aphyt.tkmi.widgets.hmi import HMIPage, HMIImage, MonitoredVariableWidgetMixin


class DispatcherMixin:
    def __init__(self, dispatcher: NSeriesThreadDispatcher = None, **kwargs):
        super().__init__(**kwargs)
        self.dispatcher = dispatcher


class MomentaryButtonMixin(DispatcherMixin):
    def __init__(self, variable_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.variable_name = variable_name

    def _on_press(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, True)

    def _on_release(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, False)


class SetButtonMixin(DispatcherMixin):
    def __init__(self, variable_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.variable_name = variable_name

    def _on_press(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, True)

    def _on_release(self, event):
        pass


class ResetButtonMixin(DispatcherMixin):
    def __init__(self, variable_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.variable_name = variable_name

    def _on_press(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, False)

    def _on_release(self, event):
        pass


class ToggleButtonMixin(DispatcherMixin):
    def __init__(self, variable_name: str = None, dispatcher: NSeriesThreadDispatcher = None, **kwargs):
        super().__init__(dispatcher, **kwargs)
        self.variable_name = variable_name

    def _on_press(self, event):
        reply = self.dispatcher.read_variable(self.variable_name)
        if reply:
            self.dispatcher.verified_write_variable(self.variable_name, False)
        else:
            self.dispatcher.verified_write_variable(self.variable_name, True)

    def _on_release(self, event):
        pass


class VariableButtonMixin(DispatcherMixin):
    def __init__(self, variable_name: str = None, value=None, dispatcher: NSeriesThreadDispatcher = None, **kwargs):
        super().__init__(dispatcher, **kwargs)
        self.variable_name = variable_name
        self.value = value

    def _on_press(self, event):
        self.dispatcher.verified_write_variable(self.variable_name, self.value)

    def _on_release(self, event):
        pass


class ImageMultiStateButton(MonitoredVariableWidgetMixin, VariableButtonMixin, tkinter.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, refresh_time,
                 state_images: Dict[int, Union[str, HMIImage]], **kwargs):
        self.log = logging.getLogger(__name__)
        self.state_images = state_images
        self.state_images_tk = {}
        for state in self.state_images:
            image = PIL.Image.open(self.state_images[state])
            self.state_images_tk[state] = PIL.ImageTk.PhotoImage(image)
        first_value = list(self.state_images_tk)[0]
        super().__init__(variable_name=variable_name,
                         value=first_value, dispatcher=dispatcher,
                         refresh_time=refresh_time,
                         master=master,
                         **kwargs)
        self.value = self.monitored_variable.value
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._value_updated()

    def _next_value(self):
        temp = list(self.state_images_tk)
        try:
            next_value = temp[temp.index(self.value) + 1]
        except (ValueError, IndexError):
            next_value = temp[0]
        return next_value

    def _value_updated(self):
        try:
            self.config(image=self.state_images_tk[self.monitored_variable.value])
        except KeyError as key_error:
            tkinter.messagebox.showerror('No State Image', 'Is this an available state?')

    def _on_press(self, event):
        self.value = self._next_value()
        super()._on_press(event)


class ImageButtonMixin(tkinter.Button):
    def __init__(self, master=None, scale=1.0, image=None, pressed_image=None, **kwargs):
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
        super().__init__(master=master, image=self.image_tk, compound='center', **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        self.config(image=self.pressed_image_tk)

    def _on_release(self, event):
        self.config(image=self.image_tk)


class PageSwitchButtonMixin(tkinter.Button):
    def __init__(self, master: tkinter.Widget, page: Union[HMIPage, str], **kwargs):
        super(PageSwitchButtonMixin, self).__init__(master=master, **kwargs)
        self.page = page
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        pass

    def _on_release(self, event):
        if type(self.page) == str:
            self.winfo_toplevel().pages[self.page].tkraise()
        else:
            self.page.tkraise()


class ImagePageSwitchButton(ImageButtonMixin, PageSwitchButtonMixin):
    def __init__(self, master: tkinter.Widget, page: Union[HMIPage, str], scale=1.0, image=None, pressed_image=None, **kwargs):
        super().__init__(master=master, page=page, image=image, pressed_image=pressed_image, scale=scale, **kwargs)
        self.config(highlightthickness=0, borderwidth=0, activebackground='#4f4f4f')

    def _on_press(self, event):
        ImageButtonMixin._on_press(self, event)

    def _on_release(self, event):
        ImageButtonMixin._on_release(self, event)
        PageSwitchButtonMixin._on_release(self, event)


class PageSwitchButton(ttk.Button, PageSwitchButtonMixin):
    def __init__(self, master: tkinter.Widget, page: Union[HMIPage, str], **kwargs):
        super().__init__(master, **kwargs)
        self.page = page
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        pass

    def _on_release(self, event):
        PageSwitchButtonMixin._on_release(self, event)


class MomentaryButton(MomentaryButtonMixin, ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class SetButton(SetButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class ResetButton(ResetButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class ToggleButton(ToggleButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

