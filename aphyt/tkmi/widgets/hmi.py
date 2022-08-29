import logging
import tkinter
from abc import ABC, abstractmethod

import PIL

from aphyt.omron import NSeriesThreadDispatcher, MonitoredVariable

DEFAULT_PADDING = 5


class HMIWidgetFrame(tkinter.Frame):
    def __init__(self, master, background=None, *args, **kwargs):
        super().__init__(master, padx=2, pady=2,  *args, **kwargs)
        if background is None:
            self.config(background=master['background'])

    def add_widget_linear(self, widget: tkinter.Widget, vertical=True):
        if vertical:
            widget.grid(row=self.grid_size()[1], padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        else:
            widget.grid(column=self.grid_size()[0] + 1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

    def add_widget_grid(self, widget: tkinter.Widget, row, column, row_span: int = 1, column_span: int = 1):
        widget.grid(row=row, column=column, rowspan=row_span, columnspan=column_span)


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


class HMIImage:
    def __init__(self, master, image=None, scale=1.0, **kwargs):
        self.image = None
        if not image:
            # image = tkinter.PhotoImage(width=1, height=1)
            self.image = PIL.Image.open('Transparent_Pixel.png')
        else:
            self.image = PIL.Image.open(image)
        self.width = int(scale * float(self.image.size[0]))
        self.height = int(scale * float(self.image.size[1]))
        self.image = self.image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        self.image_tk = PIL.ImageTk.PhotoImage(self.image)
        super().__init__(master, image=self.image_tk, compound='center', **kwargs)


class HMIPage(tkinter.Frame):
    def __init__(self, master, background=None, **kwargs):
        super().__init__(master, **kwargs)
        if background is None:
            self.config(background=master['background'])
        self.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class HMIScreen(tkinter.Tk):
    def __init__(self, window_title, dispatcher_host: str, geometry: str = None, background=None, **kwargs):
        super().__init__(**kwargs)
        self.pages = {}
        self.withdraw()
        self.iconbitmap('transparent_icon.ico')
        self.title(window_title)
        if geometry is not None:
            self.geometry(geometry)
        if background is not None:
            self.config(background=background)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.eip_instance = NSeriesThreadDispatcher()
        self.eip_instance.connect_explicit(dispatcher_host)
        self.eip_instance.register_session()

        self.update()
        self.deiconify()
