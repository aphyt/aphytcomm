__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import time
import tkinter
from tkinter import *
from tkinter import ttk
from aphyt.tkmi import helper
from aphyt.eip import EIPConnectedCIPDispatcher
from aphyt.omron import k6pm_th
import concurrent.futures
import threading
import queue
import copy


class EIPThreadDispatcher:
    def __init__(self, instance: EIPConnectedCIPDispatcher):
        self.instance = instance
        self.message_queue = queue.Queue()
        self.message_timeout = 0.5
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.futures = []
        self.status_integer = 0
        self.services = None

    def start_keep_alive(self):
        if self.instance.is_connected_explicit:
            future = self.executor.submit(
                self.instance.list_services)
            self.services = future.result()
            delay = threading.Timer(0.05, self.start_keep_alive)
            delay.start()


class Segment(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Get the current screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.unique_id = str(self)
        if screen_height > screen_width:
            max_dimension = screen_height
        else:
            max_dimension = screen_width
        self.segment_color = ttk.Style(self)
        self.theme_name = self.unique_id + '.TFrame'
        self.segment_color.configure(self.theme_name, background='blue')
        self.configure(width=max_dimension * .025, height=max_dimension * .025, style=self.theme_name)

    def set_color(self, color: str):
        self.segment_color.configure(self.theme_name, background=color)
        # self.configure(background=color)


class SegmentViewer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.box_grid = [None] * 16
        for i in range(16):
            row = i // 4 + 1
            column = i % 4 + 1
            self.box_grid[i] = Segment(self)
            self.box_grid[i].grid(row=row, column=column)
        for child in self.winfo_children():
            child.grid_configure(padx=1, pady=1)


class TemperaturePixel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Get the current screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.unique_id = str(self)
        if screen_height > screen_width:
            max_dimension = screen_height
        else:
            max_dimension = screen_width
        self.segment_color = ttk.Style(self)
        self.theme_name = self.unique_id + '.TFrame'
        self.segment_color.configure(self.theme_name, background='blue')
        self.configure(width=max_dimension * .0025, height=max_dimension * .0025, style=self.theme_name)

    def set_color(self, color: str):
        self.segment_color.configure(self.theme_name, background=color)


class TemperaturePixelViewer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # self.box_grid = [None] * 1024
        self.box_grid = []
        for i in range(1024):
            row = i // 32 + 1
            column = i % 32 + 1
            self.box_grid.append(TemperaturePixel(self))
            self.box_grid[i].grid(row=row, column=column, padx=1, pady=1)


class TemperatureCanvas(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        screen_width = master.winfo_screenwidth()
        square = 0.25
        self.width = screen_width * square
        self.canvas = tkinter.Canvas(master, width=self.width, height=self.width, bg="white")
        self.next_canvas = tkinter.Canvas(master, width=self.width, height=self.width, bg="white")
        self.pad = 0.5
        self.pixel_size = self.width/32
        self.canvas.configure(highlightthickness=0, borderwidth=0)
        self.next_canvas.configure(highlightthickness=0, borderwidth=0)
        self.canvas.grid(column=1, row=1, sticky=(E, W))
        self.next_canvas.grid(column=1, row=1, sticky=(E, W))
        self.rectangles = []
        self.next_rectangles = []
        color_string = 'green'
        for i in range(1024):
            pos_x = i % 32
            pos_y = i // 32
            x1 = pos_x * self.pixel_size + self.pad
            y1 = pos_y * self.pixel_size + self.pad
            x2 = x1 + self.pixel_size - 2 * self.pad
            y2 = y1 + self.pixel_size - 2 * self.pad
            self.rectangles.append(self.canvas.create_rectangle(x1, y1, x2, y2, width=0, fill=color_string))
            self.next_rectangles.append(self.next_canvas.create_rectangle(x1, y1, x2, y2, width=0, fill=color_string))

        self.next_canvas.grid_remove()
        for child in self.winfo_children():
            child.grid_configure(pady=10, padx=10)

    def set_color_data(self, color_list: list):
        min = 23.0
        max = 31.0
        # print(color_list)
        # self.canvas.delete(tkinter.ALL)
        for i in range(1024):
            pixel_offset = i % 64
            instance_array = i // 64
            pixel_color = color_list[instance_array][pixel_offset]
            pixel_color = k6pm_th.unsigned_integer_to_temp(pixel_color)
            slope = (650.0 - 440.0)/(max-min)
            wavelength = float(pixel_color) * slope + 440.0 - slope * min
            r, g, b = helper.wavelength_to_rgb(wavelength)
            color_string = '#' + '{:02x}'.format(r) + '{:02x}'.format(g) + '{:02x}'.format(b)
            self.next_canvas.itemconfig(self.next_rectangles[i], fill=color_string)
            # self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_string)
        self.canvas, self.next_canvas = self.next_canvas, self.canvas
        self.canvas.grid()
        self.next_canvas.grid_remove()


class ConnectFrame(ttk.Frame):
    def __init__(self, master, eip_thread_dispatcher: EIPThreadDispatcher, connect_function):
        super().__init__(master)
        self.connect_function = connect_function
        self.eip_thread_dispatcher = eip_thread_dispatcher
        self.connect_string = StringVar()
        self.connect_string.set('192.168.250.30')
        self.connect_entry = ttk.Entry(self, width=7, textvariable=self.connect_string)
        self.connect_entry.grid(column=1, row=1, columnspan=2, sticky=(W, E), padx=1)
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect)
        self.connect_button.grid(column=1, row=2, sticky=(W, E))
        self.disconnect_button = ttk.Button(self, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(column=2, row=2, sticky=(W, E))
        for child in self.winfo_children():
            child.grid_configure(pady=1)

    def connect(self):
        if not self.eip_thread_dispatcher.instance.is_connected_explicit:
            self.eip_thread_dispatcher.instance.connect_explicit(self.connect_string.get())
            self.eip_thread_dispatcher.instance.register_session()
            self.eip_thread_dispatcher.start_keep_alive()
            self.connect_function()

    def disconnect(self):
        self.eip_thread_dispatcher.executor.submit(
                self.eip_thread_dispatcher.instance.close_explicit)
        # self.eip_thread_dispatcher.instance.close_explicit()


class Screen(Tk):
    def __init__(self):
        super().__init__()
        self.title("K6PM Visualization")
        self.mainframe = ttk.Frame(self, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.k6pm_instance = k6pm_th.K6PMTHEIP()
        self.k6pm_thread_dispatcher = EIPThreadDispatcher(self.k6pm_instance)

        self.temp_canvas = TemperatureCanvas(self.mainframe)
        self.temp_canvas.grid(column=1, row=1)
        self.colors = [700] * 64
        self.colors = [self.colors] * 16
        self.temp_canvas.set_color_data(self.colors)

        self.connect_box = ConnectFrame(self.mainframe, self.k6pm_thread_dispatcher, self.periodic_task)
        self.connect_box.grid(column=1, row=2)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.clean_up)

        self.mainloop()

    def calculate(self):
        self.temperature_view.set_color('blue')

    def update_color(self, value):
        # r, g, b = scale_to_rgb(float(value) * 100.0)
        r, g, b = helper.wavelength_to_rgb(float(value) * (650.0-440.0) + 440.0)
        color_string = '#' + '{:02x}'.format(r) + '{:02x}'.format(g) + '{:02x}'.format(b)
        # self.four_pack[1].set_color(color_string)
        self.four_pack.box_grid[0].set_color(color_string)

    def periodic_task(self, period=.5):
        if self.k6pm_thread_dispatcher.instance.is_connected_explicit:
            future = self.k6pm_thread_dispatcher.executor.submit(
                self.k6pm_thread_dispatcher.instance.pixel_temperatures, 1)
            self.colors = future.result()
            self.temp_canvas.set_color_data(self.colors)
            delay = threading.Timer(period, self.periodic_task)
            delay.start()

    def clean_up(self):
        self.connect_box.disconnect()
        self.after_idle(self.destroy)


if __name__ == "__main__":
    window = Screen()
