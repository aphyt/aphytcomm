__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import struct
import tkinter
from tkinter import messagebox
from tkinter import ttk

import PIL

from aphyt.omron import NSeriesThreadDispatcher

DEFAULT_PADDING = 5


class HMIPage(tkinter.ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class HMIWidgetFrame(tkinter.ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def add_widget(self, widget: tkinter.ttk.Widget, vertical=True):
        if vertical:
            widget.grid(row=self.grid_size()[1], padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        else:
            widget.grid(column=self.grid_size()[0] + 1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)


class ImagePageSwitchButton(ttk.Button):
    def __init__(self, master: HMIPage, page: HMIPage, scale=1.0, image=None, pressed_image=None, **kwargs):
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
        super().__init__(master, image=self.image_tk, compound='c', **kwargs)
        self.page = page
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

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
    def __init__(self, master, controller: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.variable_name = variable_name
        self.current_string = None
        self.type = None
        self._get_data()
        self.delay = None
        self.controller.connection_status.bind_to_session_status(self._get_data)
        self.validate_command = (self.register(self.validate_entry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.config(validate='focus', validatecommand=self.validate_command)
        self.bind("<Return>", (lambda event: self._enter_function()))

    def _get_data(self):
        if self.controller.connection_status.has_session:
            data = self.controller.read_variable(self.variable_name)
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
            self.controller.verified_write_variable(self.variable_name, value)
            success = True
        except struct.error as error:
            success = False
        except ValueError as error:
            success = False
        return success


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
