import logging
import tkinter
from typing import Dict

import PIL

from aphyt.omron import NSeriesThreadDispatcher
from aphyt.tkmi.widgets.hmi import MonitoredVariableWidgetMixin


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
                         variable_name=variable_name, refresh_time=refresh_time, **kwargs)
        self._value_updated()

    def _value_updated(self):
        try:
            self.config(image=self.state_images_tk[self.monitored_variable.value])
        except KeyError as key_error:
            tkinter.messagebox.showerror('No State Image', 'Is this an available state?')


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
