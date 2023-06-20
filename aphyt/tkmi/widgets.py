__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import logging
import os
import struct
import tkinter
from abc import ABC, abstractmethod
from numbers import Number
from tkinter import ttk, TclError
from typing import Dict, Union, SupportsRound
import PIL
from PIL import Image, ImageTk

from aphyt.omron import NSeriesThreadDispatcher, MonitoredVariable


class DispatcherMixin:
    def __init__(self, dispatcher: NSeriesThreadDispatcher = None, **kwargs):
        super().__init__(**kwargs)
        self.dispatcher = dispatcher


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


DEFAULT_PADDING = 5


class HMIWidgetFrame(tkinter.Frame):
    def __init__(self, master, background=None, *args, **kwargs):
        super().__init__(master, padx=2, pady=2, *args, **kwargs)
        if background is None:
            try:
                self.config(background=master['background'])
            except TclError:
                pass

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
        # path = os.path.dirname(__file__)
        # path = os.path.join(path, 'transparent_icon.ico')
        # self.iconbitmap(path)
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
            pass
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

    def destroy(self):
        self.eip_instance.close_explicit()
        super().destroy()


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
                 state_images: Dict[int, str], scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        self.state_images = state_images
        self.state_images_tk = {}
        for state in self.state_images:
            # image = PIL.Image.open(self.state_images[state])
            # self.state_images_tk[state] = PIL.ImageTk.PhotoImage(image)
            image = HMIImage(state_images[state], scale, scale_x, scale_y)
            self.state_images_tk[state] = image.image_tk
        first_value = list(self.state_images_tk)[0]
        super().__init__(variable_name=variable_name,
                         value=first_value, dispatcher=dispatcher,
                         refresh_time=refresh_time,
                         master=master,
                         **kwargs)
        if background is None:
            self.config(background=master['background'])
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
    def __init__(self, master=None, dispatcher: NSeriesThreadDispatcher = None,
                 variable_name: str = None,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.image = None
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.pressed_image = None
        if not image:
            # image = tkinter.PhotoImage(width=1, height=1)
            path = os.path.dirname(__file__)
            path = os.path.join(path, 'Transparent_Pixel.png')
            self.image = HMIImage(path)
        else:
            self.image = HMIImage(image, scale, scale_x, scale_y)
        if pressed_image is None:
            self.pressed_image = self.image
        else:
            self.pressed_image = HMIImage(pressed_image, scale, scale_x, scale_y)
        self.initial_image = self.image
        super().__init__(master=master, image=self.initial_image.image_tk, compound='center', **kwargs)
        if background is None:
            self.config(background=master['background'])
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        self.config(image=self.pressed_image.image_tk)

    def _on_release(self, event):
        self.config(image=self.image.image_tk)


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
            if self.winfo_toplevel().screen_change_variable is not None:
                self.winfo_toplevel().screen_change_variable.monitored_variable.value = self.page
        else:
            self.page.tkraise()
            if self.winfo_toplevel().screen_change_variable is not None:
                self.winfo_toplevel().screen_change_variable.monitored_variable.value = self.page.__class__.__name__


class ImagePageSwitchButton(ImageButtonMixin, PageSwitchButtonMixin):
    def __init__(self, master: tkinter.Widget, page: Union[HMIPage, str], scale=1.0,
                 image=None, pressed_image=None, background=None,
                 **kwargs):
        super().__init__(master=master, page=page, image=image, pressed_image=pressed_image, scale=scale, **kwargs)
        if background is None:
            background = master['background']
        self.config(background=background)
        self.config(activebackground=background)
        self.config(highlightthickness=0, borderwidth=0)

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


class ImageMomentaryButton(MonitoredVariableWidgetMixin, ImageButtonMixin, MomentaryButtonMixin):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        super().__init__(master=master,
                         dispatcher=dispatcher,
                         variable_name=variable_name,
                         image=image, pressed_image=pressed_image,
                         scale=scale, scale_x=scale_x, scale_y=scale_y, background=background,
                         **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _value_updated(self):
        if self.monitored_variable.value:
            self.config(image=self.pressed_image.image_tk)
        else:
            self.config(image=self.image.image_tk)
        
    def _on_press(self, event):
        ImageButtonMixin._on_press(self, event)
        MomentaryButtonMixin._on_press(self, event)

    def _on_release(self, event):
        ImageButtonMixin._on_release(self, event)
        MomentaryButtonMixin._on_release(self, event)


class MomentaryButton(MomentaryButtonMixin, ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class ImageMomentaryButton(MonitoredVariableWidgetMixin, ImageButtonMixin, MomentaryButtonMixin):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        super().__init__(master=master,
                         dispatcher=dispatcher,
                         variable_name=variable_name,
                         image=image, pressed_image=pressed_image,
                         scale=scale, scale_x=scale_x, scale_y=scale_y, background=background,
                         **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._value_updated()

    def _value_updated(self):
        if self.monitored_variable.value:
            self.config(image=self.pressed_image.image_tk)
        else:
            self.config(image=self.image.image_tk)

    def _on_press(self, event):
        # ImageButtonMixin._on_press(self, event)
        MomentaryButtonMixin._on_press(self, event)

    def _on_release(self, event):
        # ImageButtonMixin._on_release(self, event)
        MomentaryButtonMixin._on_release(self, event)


class ImageSetButton(MonitoredVariableWidgetMixin, ImageButtonMixin, SetButtonMixin):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        super().__init__(master=master,
                         dispatcher=dispatcher,
                         variable_name=variable_name,
                         image=image, pressed_image=pressed_image,
                         scale=scale, scale_x=scale_x, scale_y=scale_y, background=background,
                         **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._value_updated()

    def _value_updated(self):
        if self.monitored_variable.value:
            self.config(image=self.pressed_image.image_tk)
        else:
            self.config(image=self.image.image_tk)

    def _on_press(self, event):
        # ImageButtonMixin._on_press(self, event)
        SetButtonMixin._on_press(self, event)

    def _on_release(self, event):
        SetButtonMixin._on_release(self, event)


class SetButton(SetButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class ImageResetButton(MonitoredVariableWidgetMixin, ImageButtonMixin, ResetButtonMixin):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        super().__init__(master=master,
                         dispatcher=dispatcher,
                         variable_name=variable_name,
                         image=image, pressed_image=pressed_image,
                         scale=scale, scale_x=scale_x, scale_y=scale_y, background=background,
                         **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._value_updated()

    def _value_updated(self):
        if self.monitored_variable.value:
            self.config(image=self.pressed_image.image_tk)
        else:
            self.config(image=self.image.image_tk)

    def _on_press(self, event):
        # ImageButtonMixin._on_press(self, event)
        ResetButtonMixin._on_press(self, event)

    def _on_release(self, event):
        ResetButtonMixin._on_release(self, event)


class ResetButton(ResetButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


class ImageToggleButton(MonitoredVariableWidgetMixin, ImageButtonMixin, ToggleButtonMixin):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 image=None, pressed_image=None,
                 scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        super().__init__(master=master,
                         dispatcher=dispatcher,
                         variable_name=variable_name,
                         image=image, pressed_image=pressed_image,
                         scale=scale, scale_x=scale_x, scale_y=scale_y, background=background,
                         **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._value_updated()

    def _value_updated(self):
        if self.monitored_variable.value:
            self.config(image=self.pressed_image.image_tk)
        else:
            self.config(image=self.image.image_tk)

    def _on_press(self, event):
        # ImageButtonMixin._on_press(self, event)
        ToggleButtonMixin._on_press(self, event)

    def _on_release(self, event):
        # ImageButtonMixin._on_release(self, event)
        ToggleButtonMixin._on_release(self, event)


class ToggleButton(ToggleButtonMixin, tkinter.ttk.Button):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str, **kwargs):
        super().__init__(master=master, variable_name=variable_name, dispatcher=dispatcher, **kwargs)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)


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


class ImageMultiStateLamp(MonitoredVariableWidgetMixin, VisibilityMixin, tkinter.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name, refresh_time,
                 state_images: Dict[int, str], scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        self.dispatcher = dispatcher
        self.state_images = state_images
        self.state_images_tk = {}
        for state in self.state_images:
            image = HMIImage(self.state_images[state], scale, scale_x, scale_y)
            self.state_images_tk[state] = image.image_tk
        super().__init__(master=master, dispatcher=dispatcher, variable_name=variable_name,
                         refresh_time=refresh_time, **kwargs)
        if background is None:
            self.config(background=master['background'])
        self._value_updated()

    def _value_updated(self):
        try:
            self.config(image=self.state_images_tk[self.monitored_variable.value])
        except KeyError as key_error:
            tkinter.messagebox.showerror('No State Image', 'Is this an available state?')


class ImageLamp(MonitoredVariableWidgetMixin, tkinter.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name, refresh_time,
                 image_on, image_off, scale=1.0, scale_x=1.0, scale_y=1.0, background=None, **kwargs):
        self.log = logging.getLogger(__name__)
        self.image_on = HMIImage(image_on, scale, scale_x, scale_y)
        self.image_off = HMIImage(image_off, scale, scale_x, scale_y)
        super().__init__(master=master, dispatcher=dispatcher,
                         variable_name=variable_name, refresh_time=refresh_time, **kwargs)
        if background is None:
            self.config(background=master['background'])
        self._value_updated()

    def _value_updated(self):
        self.log.debug(f'ImageLamp is updated')
        if self.monitored_variable.value:
            self.config(image=self.image_on.image_tk)
        else:
            self.config(image=self.image_off.image_tk)


class DataDisplay(tkinter.ttk.Label):
    def __init__(self, master, dispatcher: NSeriesThreadDispatcher, variable_name: str,
                 decimal_places=None, delay: int = 100, **kwargs):
        super().__init__(master, **kwargs)
        self.dispatcher = dispatcher
        self.variable_name = variable_name
        self.decimal_places = decimal_places
        self.delay = delay
        self.monitored_variable = MonitoredVariable(self.dispatcher, self.variable_name)
        self._update_data()
        self.monitored_variable.bind_to_value(self._update_data)

    def _update_data(self):
        data = self.monitored_variable.value
        if isinstance(data, SupportsRound) and self.decimal_places is not None:
            data = round(data, self.decimal_places)
        data = str(data)
        self.config(text=data)


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
