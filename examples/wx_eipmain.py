import math

__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import socket
import queue

import wx
import asyncio
import xlsxwriter
from eip import n_series
import concurrent.futures
import time
import threading


# async def async_runner(function):
#     response = function
#     return response


class NSeriesDispatcher:
    def __init__(self):
        self.instance = n_series.NSeriesEIP()
        self.controller_time = None
        self.message_queue = queue.Queue()
        self.message_timeout = 0.5
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.futures = []

    def connect(self, connect_string: str, parent_frame=None):
        self.instance.connect_explicit(connect_string)
        if self.instance.is_connected_explicit:
            self.executor.submit(self.instance.register_session)
            self.executor.submit(self.instance.update_variable_dictionary)
            # self.executor.submit(self.instance.register_session)
            # self.executor.submit(self.instance.register_session)
            self.message_queue_sender()
        else:
            wx.MessageBox('Check if the IP address is correct and the device is accessible', 'Failed to connect',
                          wx.OK | wx.ICON_INFORMATION)

    def message_queue_sender(self):
        if self.instance.is_connected_explicit:
            future = self.executor.submit(self.instance.read_variable, '_CurrentTime')
            self.controller_time = future.result()
            # print(self.controller_time)
            delay = threading.Timer(0.05, self.message_queue_sender)
            delay.start()


class IPAddressBox(wx.Panel):
    def __init__(self, parent, message_dispatcher):
        super().__init__(parent)
        self.parent = parent
        self.message_dispatcher = message_dispatcher
        self.static_box = wx.StaticBox(self, wx.ID_ANY, 'Connection')
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.ip_address_field = wx.TextCtrl(self, value='192.168.250.13', size=(120, -1))

        self.connect = wx.Button(self, wx.ID_ANY, 'Connect')
        self.connect.Bind(wx.EVT_LEFT_DOWN, self.connect_down, id=self.connect.GetId())
        self.connect.Bind(wx.EVT_LEFT_UP, self.connect_up, id=self.connect.GetId())

        self.disconnect = wx.Button(self, wx.ID_ANY, 'Disconnect')
        self.disconnect.Bind(wx.EVT_LEFT_DOWN, self.disconnect_down, id=self.disconnect.GetId())
        self.disconnect.Bind(wx.EVT_LEFT_UP, self.disconnect_up, id=self.disconnect.GetId())

        self.box_sizer.Add(self.ip_address_field, border=4)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        horizontal_sizer.Add(self.connect, flag=wx.EXPAND | wx.TOP, border=4)
        horizontal_sizer.Add(self.disconnect, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(horizontal_sizer, flag=wx.EXPAND)
        self.SetSizer(self.box_sizer)

    def connect_down(self, event):
        if not self.message_dispatcher.instance.is_connected_explicit:
            ip_address = self.ip_address_field.GetLineText(0)
            self.parent.GetParent().status_bar.SetStatusText('Connecting')
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.message_dispatcher.connect(ip_address))
                self.parent.GetParent().status_bar.SetStatusText('Connected')
                self.parent.GetParent().control_box.Enable()

        event.Skip()

    def connect_up(self, event):
        event.Skip()

    def disconnect_down(self, event):
        if self.message_dispatcher.instance.is_connected_explicit:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.message_dispatcher.instance.close_explicit())
                self.parent.GetParent().status_bar.SetStatusText('Not Connected')
                self.parent.GetParent().control_box.Disable()
        event.Skip()

    def disconnect_up(self, event):
        event.Skip()


class SystemControlBox(wx.Panel):
    def __init__(self, parent, message_dispatcher):
        super().__init__(parent)
        self.message_dispatcher = message_dispatcher
        self.measurement_data = None
        self.static_box = wx.StaticBox(self, wx.ID_ANY, 'System Control')
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.resolution_label = wx.StaticText(self, label='Sampling Motion Size (mm)')
        self.resolution = wx.TextCtrl(self, value='.5', size=(120, -1))

        self.power = wx.Button(self, wx.ID_ANY, 'Power')
        self.power.Bind(wx.EVT_LEFT_DOWN, self.power_down, id=self.power.GetId())
        self.power.Bind(wx.EVT_LEFT_UP, self.power_up, id=self.power.GetId())

        self.home = wx.Button(self, wx.ID_ANY, 'Home')
        self.home.Bind(wx.EVT_LEFT_DOWN, self.home_down, id=self.home.GetId())
        self.home.Bind(wx.EVT_LEFT_UP, self.home_up, id=self.home.GetId())

        self.reverse = wx.Button(self, wx.ID_ANY, 'Reverse')
        self.reverse.Bind(wx.EVT_LEFT_DOWN, self.reverse_jog_down, id=self.reverse.GetId())
        self.reverse.Bind(wx.EVT_LEFT_UP, self.reverse_jog_up, id=self.reverse.GetId())

        self.forward = wx.Button(self, wx.ID_ANY, 'Forward')
        self.forward.Bind(wx.EVT_LEFT_DOWN, self.forward_jog_down, id=self.forward.GetId())
        self.forward.Bind(wx.EVT_LEFT_UP, self.forward_jog_up, id=self.forward.GetId())

        self.run = wx.Button(self, wx.ID_ANY, 'Run')
        self.run.Bind(wx.EVT_LEFT_DOWN, self.run_down, id=self.run.GetId())
        self.run.Bind(wx.EVT_LEFT_UP, self.run_up, id=self.run.GetId())

        self.export = wx.Button(self, wx.ID_ANY, 'Export')
        self.export.Bind(wx.EVT_LEFT_DOWN, self.export_down, id=self.export.GetId())
        self.export.Bind(wx.EVT_LEFT_UP, self.export_up, id=self.export.GetId())

        horizontal_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer_1.Add(self.power, flag=wx.EXPAND)
        horizontal_sizer_1.Add(self.home, flag=wx.EXPAND)

        horizontal_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer_2.Add(self.reverse, flag=wx.EXPAND)
        horizontal_sizer_2.Add(self.forward, flag=wx.EXPAND)

        self.box_sizer.Add(horizontal_sizer_1, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(horizontal_sizer_2, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(self.resolution_label, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(self.resolution, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(self.run, flag=wx.EXPAND | wx.TOP, border=4)
        self.box_sizer.Add(self.export, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=4)
        self.SetSizer(self.box_sizer)

    def power_down(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_power', True))
        event.Skip()

    def power_up(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_power', False))
        event.Skip()

    def home_down(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_home', True))
        event.Skip()

    def home_up(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_home', False))
        event.Skip()

    def reverse_jog_down(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_reverse', True))
        event.Skip()

    def reverse_jog_up(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_reverse', False))
        event.Skip()

    def forward_jog_down(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_forward', True))
        event.Skip()

    def forward_jog_up(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_forward', False))
        event.Skip()

    def run_down(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_run', True))
        event.Skip()

    def run_up(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.message_dispatcher.instance.write_variable('hmi_run', False))
        event.Skip()

    def export_down(self, event):
        future = \
            self.message_dispatcher.executor.submit(
                self.message_dispatcher.instance.read_variable, 'measurement_samples')
        structure_array = future.result()
        time_string = self.message_dispatcher.controller_time.strftime("%Y_%m_%d_%H_%M_%S")
        file_string = time_string + '-scan_data.xlsx'
        workbook = xlsxwriter.Workbook(file_string)
        scan_data_worksheet = workbook.add_worksheet()
        row = 0
        column = 0

        for sample in structure_array:
            scan_data_worksheet.write(row, column, sample['position'].value())
            scan_data_worksheet.write(row, column + 1, sample['measurement'].value())
            row += 1
        workbook.close()
        event.Skip()

    def export_up(self, event):
        event.Skip()


class WxEIP(wx.Frame):

    def __init__(self, *args, **kw):
        super(WxEIP, self).__init__(*args, **kw)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.message_dispatcher = NSeriesDispatcher()
        self.SetTitle("Height Scan Command Utility")
        self.status_bar = self.CreateStatusBar()

        self.status_bar.SetStatusText('Not Connected')
        self.panel = wx.Panel(self)
        self.main_layout = wx.BoxSizer(wx.VERTICAL)
        self.connection_box = IPAddressBox(self.panel, self.message_dispatcher)
        self.control_box = SystemControlBox(self.panel, self.message_dispatcher)

        self.main_layout.Add(self.connection_box, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
        self.main_layout.Add(self.control_box, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=4)

        self.SetMinSize((300, 100))
        self.panel.SetSizer(self.main_layout)
        self.main_layout.Fit(self)
        self.control_box.Disable()
        self.Centre()
        # asyncio.create_task(self.print_time())

    def on_close(self, event):
        if self.message_dispatcher.instance.is_connected_explicit:
            self.message_dispatcher.instance.close_explicit()
        event.Skip()

    # def other_task(self, event):
    #     task = asyncio.create_task(async_runner(print("H3llo")))
    #     self.exit_button.Hide()

    def write_line(self, line):
        line = str(line)+'\n'
        self.status_window.write(line)


async def main():
    app = wx.App()
    ex = WxEIP(None, style=wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    asyncio.run(main())