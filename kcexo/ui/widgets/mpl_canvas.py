# -*- coding: UTF-8 -*-

from typing import Any
import wx

from matplotlib.figure import Figure

_USE_AGG = True

if _USE_AGG :
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
else:
    from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas


class MatplotlibCanvas(FigureCanvas):
    """Simple wrapper around matplotlib to allow us to use it in our application."""
    def __init__(self, parent: Any, wxid: Any=wx.ID_ANY):
        """Create the canvas."""
        figure = self.figure = Figure()
        FigureCanvas.__init__(self, parent, wxid, figure)  # pylint:disable=too-many-function-args  # since it is ok, really

    def cleanup(self):
        """Tidy up at the end."""
        if not _USE_AGG:
            # avoid crash
            if self.renderer.gc.gfx_ctx:
                self.renderer.gc.gfx_ctx.Destroy()
                self.renderer.gc.gfx_ctx = None

    def Hide(self):
        super().Hide()


class MatplotlibPanel(wx.Panel):
  
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        self.plt = MatplotlibCanvas(self.panel)

        main_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.Add(self.plt, flag=wx.EXPAND, proportion=1)
        self.panel.SetSizer(main_box)

        frame_box = wx.BoxSizer(wx.VERTICAL)
        frame_box.Add(self.panel, flag=wx.EXPAND, proportion=1)

        self.SetSizer(frame_box)
        self.Layout()

    def draw(self, *args, **kwargs):
        self.plt.draw(*args, **kwargs)
