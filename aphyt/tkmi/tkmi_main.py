__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from tkinter import *
from tkinter import ttk
from aphyt.tkmi import helper


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


class ConnectFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.connect_string=StringVar()
        self.connect_button = ttk.Button(self, text="Connect",
                                         command=self.connect()).grid(column=3, row=3, sticky=W)

    def connect(self):
        pass


class Screen(Tk):

    def calculate(self):
        self.temperature_view.set_color('blue')

    def update_color(self, value):
        # r, g, b = scale_to_rgb(float(value) * 100.0)
        r, g, b = helper.wavelength_to_rgb(float(value) * (650.0-440.0) + 440.0)
        color_string = '#' + '{:02x}'.format(r) + '{:02x}'.format(g) + '{:02x}'.format(b)
        # self.four_pack[1].set_color(color_string)
        self.four_pack.box_grid[0].set_color(color_string)

    def __init__(self):
        super().__init__()
        self.title("K6PM Visualization")
        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # self.temperature_view = Segment(mainframe)
        # self.temperature_view.grid(column=1, row=1)

        self.four_pack = SegmentViewer(mainframe)
        self.four_pack.grid(column=1, row=3)

        feet = StringVar()
        feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
        feet_entry.grid(column=2, row=1, sticky=(W, E))

        meters = StringVar()
        ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

        ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3, sticky=W)

        ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
        ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
        ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

        ttk.Scale(mainframe, command=self.update_color).grid(column=1, row=4)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        feet_entry.focus()
        self.bind("<Return>", self.calculate)

        self.mainloop()


if __name__ == "__main__":
    window = Screen()
