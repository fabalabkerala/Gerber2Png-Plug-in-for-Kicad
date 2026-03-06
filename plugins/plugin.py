import wx
import pcbnew

from .thread import *
from .result_event import *
from .process import *

class KiCadToGerber2PngForm(wx.Frame):
    def __init__(self):
        wx.Dialog.__init__(
            self,
            None,
            id=wx.ID_ANY,
            title=u"Gerber2Png is processing...",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_gaugeStatus = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(
                300, 20), wx.GA_HORIZONTAL)
        self.m_gaugeStatus.SetValue(0)
        bSizer1.Add(self.m_gaugeStatus, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        bSizer1.Fit(self)

        self.Centre(wx.BOTH)

        EVT_RESULT(self, self.updateDisplay)
        Gerber2PngThread(self)

    def updateDisplay(self, status):
        if status.data == -1:
            pcbnew.Refresh()
            self.Destroy()
        else:
            self.m_gaugeStatus.SetValue(int(status.data))


class Gerber2PngPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        self.name = "Gerber2Png Plug-in for KiCad"  # Plugin name
        self.category = "Manufacturing"  # Descriptive category name
        self.description = "Export to PNG by sending files to Gerber2Png with just one click."  # Description of the plugin and its functionality
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True  # Optional, default is False
        self.icon_file_name = os.path.join(
            os.path.dirname(__file__), 'icon.png')  # Optional, default is ""
        self.dark_icon_file_name = os.path.join(
            os.path.dirname(__file__), 'icon.png')

    def Run(self):
        # Plugin entry function executed when the user runs it
        KiCadToGerber2PngForm().Show()
