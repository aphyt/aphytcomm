__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import logging
import struct
import tkinter
from tkinter import messagebox
from tkinter import ttk
from abc import ABC, abstractmethod
import PIL
from aphyt.omron import NSeriesThreadDispatcher, MonitoredVariable
from typing import Dict

DEFAULT_PADDING = 5


class HMIPage(tkinter.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')


class HMIWidgetFrame(tkinter.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padx=2, pady=2, *args, **kwargs)

    def add_widget_linear(self, widget: tkinter.Widget, vertical=True):
        if vertical:
            widget.grid(row=self.grid_size()[1], padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        else:
            widget.grid(column=self.grid_size()[0] + 1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

    def add_widget_grid(self, widget: tkinter.Widget, row, column, row_span: int = 1, column_span: int = 1):
        widget.grid(row=row, column=column, rowspan=row_span, columnspan=column_span)


class MonitoredVariableWidgetMixin(ABC):
    def __init__(self,
                 dispatcher: NSeriesThreadDispatcher,
                 variable_name: str,
                 refresh_time=0.5,
                 **kwargs):
        super().__init__(**kwargs)
        self.log = logging.getLogger(__name__)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.refresh_time = refresh_time
        self.monitored_variable = MonitoredVariable(self.dispatcher, self.variable_name, self.refresh_time)
        self.monitored_variable.bind_to_value(self._value_updated)
        self.dispatcher.add_monitored_variable(self.monitored_variable)

    @abstractmethod
    def _value_updated(self):
        pass


class VisibilityMixin(tkinter.Widget):
    def __init__(self, dispatcher: NSeriesThreadDispatcher, visibility_variable, refresh_time=0.5, **kwargs):
        super().__init__(**kwargs)
        self.log = logging.getLogger(__name__)
        self.dispatcher = dispatcher
        self.visibility_variable = visibility_variable
        self.refresh_time = refresh_time
        self.monitored_visibility_variable = MonitoredVariable(self.dispatcher,
                                                               self.visibility_variable,
                                                               self.refresh_time)
        self.monitored_visibility_variable.bind_to_value(self._update)

    def _update(self):
        if self.monitored_visibility_variable.value:
            self.show()
        else:
            self.hide()

    def show(self):
        if self.winfo_manager() == 'grid':
            self.grid()
        elif self.winfo_manager() == 'place':
            self.place()

    def hide(self):
        if self.winfo_manager() == 'grid':
            self.grid_forget()
        elif self.winfo_manager() == 'place':
            self.place_forget()


class ImageMultiStateLamp(MonitoredVariableWidgetMixin, tkinter.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name, refresh_time,
                 state_images: Dict[int, str], **kwargs):
        self.log = logging.getLogger(__name__)
        self.state_images = state_images
        self.state_images_tk = {}
        for state in self.state_images:
            image = PIL.Image.open(self.state_images[state])
            self.state_images_tk[state] = PIL.ImageTk.PhotoImage(image)
        super().__init__(master=master, dispatcher=dispatcher,
                         variable_name=variable_name, refresh_time=refresh_time)
        self._value_updated()

    def _value_updated(self):
        try:
            self.config(image=self.state_images_tk[self.monitored_variable.value])
        except KeyError as key_error:
            tkinter.messagebox.showerror('No State Image', 'Is this an available state?')


class ImageMultiStateButton(MonitoredVariableWidgetMixin, tkinter.Button):
    def _value_updated(self):
        pass


class ImageLamp(MonitoredVariableWidgetMixin, tkinter.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name, refresh_time,
                 image_on, image_off, **kwargs):
        self.log = logging.getLogger(__name__)
        self.image_on = PIL.Image.open(image_on)
        self.image_off = PIL.Image.open(image_off)
        self._image_on_tk = PIL.ImageTk.PhotoImage(self.image_on)
        self._image_off_tk = PIL.ImageTk.PhotoImage(self.image_off)
        super().__init__(master=master, dispatcher=dispatcher,
                         variable_name=variable_name, refresh_time=refresh_time)
        self._value_updated()

    def _value_updated(self):
        self.log.debug(f'ImageLamp is updated')
        if self.monitored_variable.value:
            self.config(image=self._image_on_tk)
        else:
            self.config(image=self._image_off_tk)


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


class DataEdit(tkinter.ttk.Entry):
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


class DataDisplay(tkinter.ttk.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self._update_data()
        self.delay = None
        self.dispatcher.connection_status.bind_to_session_status(self._update_data)

    def _update_data(self):
        if self.dispatcher.connection_status.has_session:
            data = str(self.dispatcher.read_variable(self.variable_name))
            self.config(text=data)
            self.after(100, self._update_data)
            # self.delay = threading.Timer(0.1, self._update_data)
            # self.delay.start()


class PushButton(tkinter.ttk.Button):
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
