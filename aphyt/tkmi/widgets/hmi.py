import logging
import os
import tkinter
from tkinter import ttk
from abc import ABC, abstractmethod
import PIL
from aphyt.omron import NSeriesThreadDispatcher, MonitoredVariable
from aphyt.tkmi.widgets import *

DEFAULT_PADDING = 5


class HMIWidgetFrame(tkinter.Frame):
    def __init__(self, master, background=None, *args, **kwargs):
        super().__init__(master, padx=2, pady=2,  *args, **kwargs)
        if background is None:
            self.config(background=master['background'])

    def add_widget_linear(self, widget: tkinter.Widget, vertical=True,
                          pad_x=None, pad_y=None, **kwargs):
        if pad_x is None:
            pad_x = DEFAULT_PADDING
        if pad_y is None:
            pad_y = DEFAULT_PADDING
        if vertical:
            widget.grid(row=self.grid_size()[1] + 1, padx=pad_x,
                        pady=pad_y, sticky='n', **kwargs)
        else:
            widget.grid(column=self.grid_size()[0] + 1, padx=pad_x,
                        pady=pad_y, sticky='w', **kwargs)

    def add_widget_grid(self, widget: tkinter.Widget, row, column,
                        row_span: int = 1, column_span: int = 1,
                        pad_x=None, pad_y=None, **kwargs):
        if pad_x is None:
            pad_x = DEFAULT_PADDING
        if pad_y is None:
            pad_y = DEFAULT_PADDING
        widget.grid(row=row, column=column,
                    rowspan=row_span, columnspan=column_span,
                    padx=pad_x, pady=pad_y, **kwargs)
        if hasattr(widget, 'visibility_variable'):
            if widget.visibility_variable is not None:
                widget.hide()
                widget.visibility_update()


class MonitoredVariableWidgetMixin(ABC):
    def __init__(self,
                 dispatcher: NSeriesThreadDispatcher = None,
                 variable_name: str = None,
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
    def __init__(self,
                 visibility_variable=None,
                 refresh_time=0.5, **kwargs):
        super().__init__(**kwargs)
        self.visibility_variable = visibility_variable
        self.refresh_time = refresh_time
        self.invisible_widget = ImageWidget()
        self.visible = False
        if self.visibility_variable is not None:
            self.monitored_visibility_variable = MonitoredVariable(self.dispatcher,
                                                                   self.visibility_variable,
                                                                   self.refresh_time)
            self.monitored_visibility_variable.bind_to_value(self.visibility_update)
            # self.after(50, self.wait_visibility)
            self.visibility_update()

    def visibility_update(self):
        if self.monitored_visibility_variable.value:
            self.show()
        else:
            self.hide()

    def show(self):
        self.invisible_widget.grid_remove()
        self.grid()

    def hide(self):
        self.invisible_widget.set_size(self.winfo_reqwidth(),
                                       self.winfo_reqheight())
        self.invisible_widget.grid(self.grid_info())
        self.grid_remove()


class ImageWidget(tkinter.Label):
    def __init__(self, master=None, image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.image = None
        self.pressed_image = None
        if not image:
            # image = tkinter.PhotoImage(width=1, height=1)
            path = os.path.dirname(__file__)
            path = os.path.join(path, 'Transparent_Pixel.png')
            self.image = HMIImage(path)
        else:
            self.image = HMIImage(image, scale, scale_x, scale_y)
        super().__init__(master=master, image=self.image.image_tk, borderwidth=0, highlightthickness=0,
                         **kwargs)

    def set_size(self, width: int = 1, height: int = 1):
        self.image.set_size(width, height)
        self.config(image=self.image.image_tk)


class HMIImage:
    def __init__(self, image=None, scale=1.0, scale_x=1.0, scale_y=1.0, **kwargs):
        # ToDo scale, scale_x, scale_y?
        self.image = None
        path = os.path.dirname(__file__)
        if image is None:
            path = os.path.join(path, 'Transparent_Pixel.png')
            self.image = PIL.Image.open(path)
        else:
            # path = os.path.join(path, image)
            self.image = PIL.Image.open(image)
        self.width = int(scale * scale_x * float(self.image.size[0]))
        self.height = int(scale * scale_y * float(self.image.size[1]))
        self.image = self.image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        self.image_tk = PIL.ImageTk.PhotoImage(self.image)
        # super().__init__(master, image=self.image_tk, compound='center', **kwargs)

    def resize(self, scale=1.0, scale_x=1.0, scale_y=1.0):
        self.width = int(scale * scale_x * float(self.image.size[0]))
        self.height = int(scale * scale_y * float(self.image.size[1]))
        self.image = self.image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        self.image_tk = PIL.ImageTk.PhotoImage(self.image)

    def set_size(self, width: int = 1, height: int = 1):
        self.width = width
        self.height = height
        self.image = self.image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        self.image_tk = PIL.ImageTk.PhotoImage(self.image)


class HMIPage(tkinter.Frame):
    def __init__(self, master, background=None, **kwargs):
        super().__init__(master, **kwargs)
        if background is None:
            self.config(background=master['background'])
        self.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class HMIControllerPageChange(MonitoredVariableWidgetMixin):
    def __init__(self, screen: 'HMIScreen', **kwargs):
        super(HMIControllerPageChange, self).__init__(**kwargs)
        self.screen = screen

    def _value_updated(self):
        self.screen.change_page(self.monitored_variable.value)


class HMIScreen(tkinter.Tk):
    def __init__(self, window_title,
                 dispatcher_host: str,
                 initial_page: str,
                 dictionary_file=None,
                 geometry: str = None,
                 background=None,
                 screen_change_variable=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.initial_page = initial_page
        self.pages = {}
        self.withdraw()
        self.iconbitmap('transparent_icon.ico')
        self.title(window_title)
        self.screen_change_variable = screen_change_variable
        if geometry is not None:
            self.geometry(geometry)
        if background is not None:
            self.config(background=background)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.eip_instance = NSeriesThreadDispatcher()
        self.eip_instance.connect_explicit(dispatcher_host)
        self.eip_instance.register_session()
        if dictionary_file is not None:
            self.eip_instance.load_dictionary_file_if_present(dictionary_file)
        else:
            self.eip_instance.update_variable_dictionary()
        self.update()
        self.deiconify()

    def show_front_page(self):
        self.change_page(self.initial_page)
        if self.screen_change_variable is not None:
            if type(self.screen_change_variable) == str:
                self.screen_change_variable = HMIControllerPageChange(self,
                                                                      dispatcher=self.eip_instance,
                                                                      variable_name=self.screen_change_variable,
                                                                      refresh_time=0.05)
                self.screen_change_variable.monitored_variable.value = self.initial_page

    def change_page(self, page: str):
        self.pages[page].tkraise()
