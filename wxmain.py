import math

__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import wx
import asyncio
import binascii
from nxmessageservice.nxmessagedispatcher import *


async def async_runner(function):
    response = function
    return response


class WxNxMessageDemo(wx.Frame):

    def __init__(self, *args, **kw):
        super(WxNxMessageDemo, self).__init__(*args, **kw)

        self.dispatcher = NXMessageDispatcher()
        self.panel = wx.Panel(self)

        self.ip_address_label = wx.StaticText(self.panel, label='IP Address')
        self.ip_address_field = wx.TextCtrl(self.panel, value='192.168.250.15', size=(120, -1))
        self.get_status = wx.Button(self.panel, wx.ID_ANY, 'Get Status')
        self.Bind(wx.EVT_BUTTON, self.get_status_method, id=self.get_status.GetId())

        self.status_window = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)

        self.main_layout = wx.BoxSizer(wx.HORIZONTAL)

        self.control_box = wx.BoxSizer(wx.VERTICAL)

        self.control_box.Add(self.ip_address_label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.control_box.Add(self.ip_address_field, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.control_box.Add(self.get_status, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=4)

        self.main_layout.Add(self.control_box, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=4)

        self.status_box = wx.BoxSizer(wx.VERTICAL)
        self.status_box.Add(self.status_window, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)

        self.main_layout.Add(self.status_box, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=4)

        self.panel.SetSizer(self.main_layout)

        self.SetTitle("NX Message Demo")
        self.Centre()

    def get_status_method(self, event):
        try:
            ip_address = self.ip_address_field.GetLineText(0)
            self.status_window.Clear()
            self.dispatcher.connect(ip_address)
            input_data = binascii.hexlify(self.dispatcher.get_input_data().data)
            output_data = binascii.hexlify(self.dispatcher.get_output_data().data)
            self.write_line("Input Data Is:")
            self.write_line(input_data)
            self.write_line("Output Data Is:")
            self.write_line(output_data)
            coupler = self.dispatcher.read_nx_object(unit=0, index=0x1000, sub_index=2, control_field=0).data[2:]
            number_of_cards = self.dispatcher.read_nx_object(unit=0, index=0x2003, sub_index=3, control_field=0).data[2:]
            number_of_cards = int(math.log(int.from_bytes(number_of_cards, 'little')+1)/math.log(2))-1
            self.write_line("{} has {} cards:".format(coupler.decode('ascii').strip(), number_of_cards))
            for i in range(number_of_cards):
                name = self.dispatcher.read_nx_object(unit=i+1, index=0x1000, sub_index=2, control_field=0).data[2:]
                self.write_line(name.decode('ascii').strip())
        except socket.error:
            print("SHIT")
        try:
            self.dispatcher.disconnect()
        except socket.error:
            pass

    def other_task(self, event):
        task = asyncio.create_task(async_runner(print("H3llo")))
        self.exit_button.Hide()

    def write_line(self, line):
        line = str(line)+'\n'
        self.status_window.write(line)


async def main():
    app = wx.App()
    ex = WxNxMessageDemo(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    asyncio.run(main())
