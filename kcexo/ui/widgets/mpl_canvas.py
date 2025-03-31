# -*- coding: UTF-8 -*-
import warnings
from typing import Any
import wx
import wx.lib.newevent as NE

from matplotlib.axes import Axes
from matplotlib.figure import Figure

_USE_AGG = True

if _USE_AGG :
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
else:
    from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas


CanvasMotionEvent, EV_MOUSE_MOTION = NE.NewCommandEvent()


class MatplotlibCanvas(FigureCanvas):
    """Simple wrapper around matplotlib to allow us to use it in our application."""
    def __init__(self, parent: Any, 
                 wxid: Any=wx.ID_ANY,
                 allow_drag_move: bool=True,
                 allow_scroll_zoom: bool=True):
        """Create the canvas."""
        figure = self.figure = Figure()
        FigureCanvas.__init__(self, parent, wxid, figure)  # pylint:disable=too-many-function-args  # since it is ok, really
        
        self.canvas_cur_xlim = None
        self.canvas_cur_ylim = None
        self.canvas_press = None
        self.canvas_xpress = None
        self.canvas_ypress = None
        self.ax = None
        
        if allow_drag_move:
            self.mpl_connect('scroll_event', self.on_canvas_scroll)
            self.mpl_connect('button_press_event', self.on_canvas_press)
            self.mpl_connect('button_release_event', self.on_canvas_release)
            
        if allow_scroll_zoom:
            self.mpl_connect('motion_notify_event', self.on_canvas_motion)

    def cleanup(self):
        """Tidy up at the end."""
        if not _USE_AGG:
            # avoid crash
            if self.renderer.gc.gfx_ctx:
                self.renderer.gc.gfx_ctx.Destroy()
                self.renderer.gc.gfx_ctx = None

    def Hide(self):
        super().Hide()
        
    def on_canvas_scroll(self, event):
        """Handle image zoom using mouse scroll wheel"""
        if self.ax is None:
            return
        base_scale = .5
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        # cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        # cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            wx.MessageBox("Something has gone wrong with the zoom.\nPlease raise an issue ticket with the developers.", wx.OK|wx.CENTRE|wx.ICON_ERROR)
        # set new limits
        self.ax.set_xlim([xdata - (xdata-cur_xlim[0]) / scale_factor, xdata + (cur_xlim[1]-xdata) / scale_factor])
        self.ax.set_ylim([ydata - (ydata-cur_ylim[0]) / scale_factor, ydata + (cur_ylim[1]-ydata) / scale_factor])
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            self.draw() # force re-draw

    def on_canvas_press(self, event):
        """Handle image click-and-drag initial mouse click event"""
        if self.ax is None:
            return
        if event.inaxes != self.ax: 
            return
        self.canvas_cur_xlim = self.ax.get_xlim()
        self.canvas_cur_ylim = self.ax.get_ylim()
        self.canvas_press =event.xdata, event.ydata
        self.canvas_xpress, self.canvas_ypress = self.canvas_press

    def on_canvas_release(self, event):
        """Handle image click-and-drag mouse release event"""
        self.canvas_press = None
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            self.draw()

    def on_canvas_motion(self, event):
        """Handle image click-and-drag event"""
        if self.ax is None:
            return
        if event.inaxes != self.ax: 
            return
        if self.canvas_press is None: 
            wx.PostEvent(self, CanvasMotionEvent(wx.ID_ANY, xdata=event.xdata, ydata=event.ydata))    
            return
        
        dx = event.xdata - self.canvas_xpress
        dy = event.ydata - self.canvas_ypress
        self.canvas_cur_xlim -= dx
        self.canvas_cur_ylim -= dy
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            
            self.ax.set_xlim(self.canvas_cur_xlim)
            self.ax.set_ylim(self.canvas_cur_ylim)

            self.draw()
        wx.PostEvent(self, CanvasMotionEvent(wx.ID_ANY, xdata=event.xdata, ydata=event.ydata))

    def add_subplot(self, *argv, **kwargs) -> Axes:
        """Pass-through for creation of axes and subplots"""
        self.ax = self.figure.add_subplot(*argv, **kwargs)
        return self.ax

class MatplotlibPanel(wx.Panel):
    """Panel wrapper for the matplotlib canvas"""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        self.canvas = MatplotlibCanvas(self.panel)

        main_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.Add(self.canvas, flag=wx.EXPAND, proportion=1)
        self.panel.SetSizer(main_box)

        frame_box = wx.BoxSizer(wx.VERTICAL)
        frame_box.Add(self.panel, flag=wx.EXPAND, proportion=1)

        self.SetSizer(frame_box)
        self.Layout()
