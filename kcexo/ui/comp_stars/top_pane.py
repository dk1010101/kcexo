# -*- coding: UTF-8 -*-
from typing import Tuple, Any

import wx

from astropy.visualization import SqrtStretch, LogStretch, AsinhStretch, ZScaleInterval, SquaredStretch, MinMaxInterval, SinhStretch, LinearStretch

from kcexo.ui.widgets.new_event import new_command_event
from kcexo.ui.widgets.range_slider import RangeSlider
from kcexo.ui.widgets.filter_control import ValFilter
from kcexo.ui.widgets.mpl_canvas import MatplotlibPanel


FilterChangeEvent, EV_FILTER_CHANGE = new_command_event()
ImageXFlipEvent, EV_FILTER_IMG_X_FLIP = new_command_event()
ImageYFlipEvent, EV_FILTER_IMG_Y_FLIP = new_command_event()
ImageStretchEvent, EV_FILTER_IMG_STRETCH = new_command_event()
ImageStretchResetEvent, EV_FILTER_IMG_STRETCH_RESET = new_command_event()
ImageResetEvent, EV_FILTER_IMG_RESET = new_command_event()


class TopPanel(wx.Panel):
    """Top pane panel for the comparator star tool"""
    def __init__(self, parent, wid=wx.ID_ANY, 
                 background_colour: wx.Colour=wx.WHITE, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 name='topPanel'):
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name)

        self.stretch_prev_vmin=65535  # some bigish number
        self.stretch_prev_vmax=0
        self.stretch_max = 0
        self.stretch_min = 65535

        self.controls_collection = []
        self.background_colour = background_colour
        
        self.canvas_panel: wx.Panel = None
        self.cb_image_stretch: wx.ComboBox = None
        self.lbl_image_stretch_min: wx.StaticText = None
        self.slider_image_stretch: RangeSlider = None
        self.lbl_image_stretch_max: wx.StaticText = None
        self.bt_image_stretch_apply: wx.Button = None
        self.bt_image_stretch_reset: wx.Button = None
        self.cb_flip_x: wx.ComboBox = None
        self.cb_flip_y: wx.ComboBox = None
        self.bt_image_reset: wx.Button = None
        self.flt_dist: ValFilter = None
        self.flt_bv: ValFilter = None
        self.flt_b: ValFilter = None
        self.flt_v: ValFilter = None
        self.flt_r: ValFilter = None
        
        panel_sizer = wx.FlexGridSizer(2, 2, 3, 3)
    
        ############################################
        # top left - canvas
        self.canvas_panel = MatplotlibPanel(self, wx.ID_ANY, style=wx.NO_BORDER)
        self.figure = self.canvas_panel.canvas.figure
        self.canvas = self.canvas_panel.canvas
        panel_sizer.Add(self.canvas_panel, 0, wx.EXPAND, 1)
                
        ############################################
        # top right - filter panel
        filter_panel = self.create_filter_panel(self, background_colour)
        panel_sizer.Add(filter_panel, 0, wx.EXPAND, 1)

        ############################################
        # bottom left - image stretch and reset panel
        im_panel = self.create_image_manipulation_panel(self, background_colour)
        panel_sizer.Add(im_panel, 0, wx.EXPAND | wx.BOTTOM, 0)

        ############################################
        # bottom right
        panel_sizer.Add((0,0), 0, wx.EXPAND, 0)
        
        ############################################
        panel_sizer.AddGrowableRow(0)
        panel_sizer.AddGrowableCol(0)
        ############################################
        self.SetAutoLayout(True)
        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)
        self.Layout()
        
        self.controls_collection.append(self.canvas_panel)
     
    def create_image_manipulation_panel(self, parent: wx.Panel, bg_col: wx.Colour) -> wx.Panel:
        """Creates the panel used to stretch, flip etc the image."""
        
        panel = wx.Panel(parent, -1)
        panel.SetBackgroundColour(bg_col)
        
        panel_sizer = wx.FlexGridSizer(1, 19, 0, 0)
        
        ############################################
        # 1 - space
        panel_sizer.Add((10, 15), 0, 0, 0)
        
        # 2 - "Image Stretch" label
        label_13 = wx.StaticText(panel, wx.ID_ANY, "Image Stretch ", style=wx.ALIGN_RIGHT)
        panel_sizer.Add(label_13, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 3 - space
        panel_sizer.Add((5, 15), 0, 0, 0)

        # 4 - stretch combo box
        self.cb_image_stretch = wx.ComboBox(panel, wx.ID_ANY, choices=["linear", "log", "sinh", "asinh", "square", "sqrt"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SIMPLE)
        self.cb_image_stretch.SetMinSize((60, 25))
        self.cb_image_stretch.SetSelection(2)
        self.cb_image_stretch.SetToolTip(wx.ToolTip("Algorithm to use to stretch the image"))
        panel_sizer.Add(self.cb_image_stretch, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        # sz = self.cb_image_stretch.GetMinHeight()

        # 5 - space
        panel_sizer.Add((15, 15), 0, 0, 0)

        # 6 - text box, lower limit
        self.txt_stretch_lower_limit = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
        self.txt_stretch_lower_limit.SetMinSize((45, -1))
        self.txt_stretch_lower_limit.SetToolTip(wx.ToolTip("The lower limit of the stretch range\nEnter new value and press enter to change"))
        panel_sizer.Add(self.txt_stretch_lower_limit, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 0)
        
        # 7 - label "/"
        label_s1 = wx.StaticText(panel, wx.ID_ANY, "/", style=wx.ALIGN_CENTER)
        panel_sizer.Add(label_s1, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 8 - slider lower value label
        self.lbl_image_stretch_min = wx.StaticText(panel, wx.ID_ANY, "        ", style=wx.ALIGN_RIGHT)
        self.lbl_image_stretch_min.SetMinSize((35, -1))
        self.lbl_image_stretch_min.SetToolTip(wx.ToolTip("The lower value used to stretch the image\nChanged by the slider"))
        panel_sizer.Add(self.lbl_image_stretch_min, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 9 - slider
        self.slider_image_stretch = RangeSlider(panel, lowValue=0, highValue=65535, minValue=0, maxValue=65535)
        self.slider_image_stretch.SetBackgroundColour(bg_col)
        self.slider_image_stretch.SetMinSize((200, 15))
        panel_sizer.Add(self.slider_image_stretch, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 10 - slide upper value label
        self.lbl_image_stretch_max = wx.StaticText(panel, wx.ID_ANY, "        ", style=wx.ALIGN_LEFT)
        self.lbl_image_stretch_max.SetMinSize((35, -1))
        self.lbl_image_stretch_max.SetToolTip(wx.ToolTip("The upper value used to stretchthe image\nChanged by the slider"))
        panel_sizer.Add(self.lbl_image_stretch_max, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 11 - label "/"
        label_s2 = wx.StaticText(panel, wx.ID_ANY, "/", style=wx.ALIGN_CENTER)
        panel_sizer.Add(label_s2, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 12 - text box, upper limit
        self.txt_stretch_upper_limit = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER|wx.TE_LEFT)
        self.txt_stretch_upper_limit.SetMinSize((45, -1))
        self.txt_stretch_upper_limit.SetToolTip(wx.ToolTip("The upper limit of the stretch range\nEnter new value and press enter to change"))
        panel_sizer.Add(self.txt_stretch_upper_limit, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 0)
        
        # 13 - space
        panel_sizer.Add((15, 15), 0, 0, 0)

        # 14 - "Apply" button
        self.bt_image_stretch_apply = wx.Button(panel, wx.ID_ANY, "Apply")
        self.bt_image_stretch_apply.SetToolTip(wx.ToolTip("Apply the changes to the image\nThis will also reset the zoom"))
        panel_sizer.Add(self.bt_image_stretch_apply, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        # 15 - "Reset" buttone
        self.bt_image_stretch_reset = wx.Button(panel, wx.ID_ANY, "Reset")
        self.bt_image_stretch_reset.SetToolTip(wx.ToolTip("Reset stretch to the initial (potential `ideal`) values\nThis will also reset the zoom"))
        panel_sizer.Add(self.bt_image_stretch_reset, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # 16 - space
        panel_sizer.Add((30, 15), 0, 0, 0)

        # 17 - "Flip X" check box
        self.cb_flip_x = wx.CheckBox(panel, wx.ID_ANY, "Flip X")
        self.cb_flip_x.SetToolTip(wx.ToolTip("Mirror the image"))
        panel_sizer.Add(self.cb_flip_x, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        
        # 18 - "Flip Y" check box
        self.cb_flip_y = wx.CheckBox(panel, wx.ID_ANY, "Flip Y")
        self.cb_flip_y.SetToolTip(wx.ToolTip("Flip the image"))
        panel_sizer.Add(self.cb_flip_y, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # 19 - "Reset Zoom" button
        self.bt_image_reset = wx.Button(panel, wx.ID_ANY, "Reset Zoom")
        self.bt_image_reset.SetToolTip(wx.ToolTip("Reset to fully zoomed out view"))
        panel_sizer.Add(self.bt_image_reset, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        ############################################

        panel_sizer.AddGrowableCol(9)
        
        ########
        # events
        # self.slider_image_stretch.Bind(wx.EVT_LEFT_UP, self.on_slider_image_stretch)
        # self.bt_image_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        # self.bt_image_stretch_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_reset)
        # self.bt_image_stretch_apply.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        # self.cb_flip_x.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        # self.cb_flip_y.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        self.bt_image_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_reset)
        self.bt_image_stretch_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch_reset)
        self.bt_image_stretch_apply.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        self.cb_flip_x.Bind(wx.EVT_CHECKBOX, self.on_cb_flip_x)
        self.cb_flip_y.Bind(wx.EVT_CHECKBOX, self.on_cb_flip_y)
        self.slider_image_stretch.Bind(wx.EVT_LEFT_UP, self.on_slider_image_stretch)
        self.txt_stretch_lower_limit.Bind(wx.EVT_TEXT_ENTER, self.on_txt_stretch_lower_change)
        self.txt_stretch_lower_limit.Bind(wx.EVT_KILL_FOCUS, self.on_txt_stretch_lower_lost_focus)
        self.txt_stretch_upper_limit.Bind(wx.EVT_TEXT_ENTER, self.on_txt_stretch_upper_change)
        self.txt_stretch_upper_limit.Bind(wx.EVT_KILL_FOCUS, self.on_txt_stretch_upper_lost_focus)
        
        #####
        # add to enable/disable list
        self.controls_collection.append(self.cb_image_stretch)
        self.controls_collection.append(self.lbl_image_stretch_min)
        self.controls_collection.append(self.slider_image_stretch)
        self.controls_collection.append(self.lbl_image_stretch_max)
        self.controls_collection.append(self.bt_image_stretch_apply)
        self.controls_collection.append(self.bt_image_stretch_reset)
        self.controls_collection.append(self.cb_flip_x)
        self.controls_collection.append(self.cb_flip_y)
        self.controls_collection.append(self.bt_image_reset)
        
        panel.SetSizer(panel_sizer)
        
        return panel


    def create_filter_panel(self, parent: wx.Panel, bg_col: wx.Colour) -> wx.Panel:
        """Create the panel that will be on the right of the top pane and will be used to get filtering properties."""
        panel = wx.Panel(parent, -1)
        panel.SetBackgroundColour(bg_col)  # should be bg_col
        
        # this will allow us to have the filters at the top and not have then stretch
        panel_sizer = wx.FlexGridSizer(2, 1, 0, 0)
                
        filters_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        filters_sizer.Add(250, 0, 0) # set the width
        ############################################
        ### row 1 - Distance - title
                
        self.flt_dist = ValFilter(panel, wx.ID_ANY, 
                                  "Distance", has_nan=False, 
                                  colour=bg_col, 
                                  show_titles=True, 
                                  titles=["Target\nValues", "Use", " Inc\nNaN"])
        filters_sizer.Add(self.flt_dist, 0, wx.EXPAND, 0)
        
        ### row 2 - blank
        filters_sizer.Add((0, 5), 0, 0, 0)
        
        ############################################
        ### row 3 - B-V - title
        
        self.flt_bv = ValFilter(panel, wx.ID_ANY, "B-V", has_nan=True, colour=bg_col)
        filters_sizer.Add(self.flt_bv, 0, wx.EXPAND, 0)
        
        ### row 4 - blank
        filters_sizer.Add((0, 5), 0, 0, 0)
        
        ############################################
        ### row 5 - B - title
        
        self.flt_b = ValFilter(panel, wx.ID_ANY, "B", has_nan=True, colour=bg_col)
        filters_sizer.Add(self.flt_b, 0, wx.EXPAND, 0)
        
        ### row 6 - blank
        filters_sizer.Add((0, 5), 0, 0, 0)

        ############################################
        ### row 7 - V - title
        
        self.flt_v = ValFilter(panel, wx.ID_ANY, "V", has_nan=True, colour=bg_col)
        filters_sizer.Add(self.flt_v, 0, wx.EXPAND, 0)
        
        ### row 8 - blank
        filters_sizer.Add((0, 5), 0, 0, 0)

        ############################################
        ### row 9 - R - title
        
        self.flt_r = ValFilter(panel, wx.ID_ANY, "R", has_nan=True, colour=bg_col)
        filters_sizer.Add(self.flt_r, 0, wx.EXPAND, 0)
        
        ### row 10 - blank
        filters_sizer.Add((0, 5), 0, 0, 0)
        
        ############################################
        panel_sizer.Add(filters_sizer, 0, wx.EXPAND, 0)
        panel_sizer.Add((0, 0), 0, 0, 0)
        
        panel_sizer.AddGrowableRow(1)
        
        ########
        # events        
        self.flt_dist.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.flt_bv.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.flt_b.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.flt_v.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.flt_r.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
    
        #####
        # add to enable/disable list
        
        self.controls_collection.append(self.flt_dist)
        self.controls_collection.append(self.flt_bv)
        self.controls_collection.append(self.flt_b)
        self.controls_collection.append(self.flt_v)
        self.controls_collection.append(self.flt_r)
        
        panel.SetSizerAndFit(panel_sizer)
        
        return panel

    def set_filter_target_values(self, target_vals: dict) -> None:
        """Give a dictionary of values, set the filter target values."""
        self.flt_dist.SetTargetValue(target_vals['dist'])
        self.flt_bv.SetTargetValue(target_vals['B-V'])
        self.flt_b.SetTargetValue(target_vals['B'])
        self.flt_v.SetTargetValue(target_vals['V'])
        self.flt_r.SetTargetValue(target_vals['R'])
    
    def set_filter_minmax(self, minmax_vals: dict) -> None:
        """Give a dictionary of values, set the filter min-max values."""
        self.flt_dist.SetMinMax(*minmax_vals['dist'])
        self.flt_bv.SetMinMax(*minmax_vals['B-V'])
        self.flt_b.SetMinMax(*minmax_vals['B'])
        self.flt_v.SetMinMax(*minmax_vals['V'])
        self.flt_r.SetMinMax(*minmax_vals['R'])

    def set_initial_stretch(self, image_data) -> None:
        """Work-out the initial image stretch values and set the ui sliders appropriately."""
        interval = MinMaxInterval()
        l_vmin, l_vmax = interval.get_limits(image_data)
        self.stretch_min = l_vmin
        self.stretch_max = l_vmax
        
        self.cb_image_stretch.SetSelection(2)

        interval = ZScaleInterval()
        vmin, vmax = interval.get_limits(image_data)
        
        ld = vmin - vmin * 0.15
        if ld < l_vmin:
            ld = l_vmin
        self.txt_stretch_lower_limit.SetValue(str(int(ld)))
        self.slider_image_stretch.SetMin(int(ld))
        
        ud = vmax * 1.15
        if ud > l_vmax:
            ud = l_vmax
        self.txt_stretch_upper_limit.SetValue(str(int(ud)))
        self.slider_image_stretch.SetMax(int(ud))
        
        self.slider_image_stretch.SetValues(vmin, vmax)
        self.on_slider_image_stretch(None)

    def on_cb_filter_change(self, event):
        """If the `use` checkbox has changed value, post the change event."""
        wx.PostEvent(self, FilterChangeEvent(event.GetId()))

    def on_bt_image_reset(self, event):
        """Is the image reset has been pushed, trigger the image reset event."""
        wx.PostEvent(self, ImageResetEvent(event.GetId()))
        
    def on_bt_image_stretch_reset(self, event):
        """Is the image stretch reset has been pushed, trigger the image stretch reset event."""
        wx.PostEvent(self, ImageStretchResetEvent(event.GetId()))
        
    def on_bt_image_stretch(self, event):
        """Is the image stretch has been pushed, trigger the image stretch event."""
        wx.PostEvent(self, ImageStretchEvent(event.GetId()))
        
    def on_cb_flip_x(self, event):
        """Is the image x-axis flip has been selected, trigger the x-axis flip event."""
        wx.PostEvent(self, ImageXFlipEvent(event.GetId()))
        
    def on_cb_flip_y(self, event):
        """Is the image y-axis flip has been selected, trigger the y-axis flip event."""
        wx.PostEvent(self, ImageYFlipEvent(event.GetId()))
        
    def on_slider_image_stretch(self, event):
        """Handle the change in the image stretch slider."""
        vmin, vmax = self.slider_image_stretch.GetValues()
        self.lbl_image_stretch_min.SetLabel(str(int(vmin)))
        self.lbl_image_stretch_max.SetLabel(str(int(vmax)))
        if event:
            event.Skip()

    def on_txt_stretch_lower_change(self, event):
        vmin, vmax = self.slider_image_stretch.GetValues()
        v = int(self.txt_stretch_lower_limit.GetValue())
        if v < self.stretch_min:
            v = self.stretch_min
            self.txt_stretch_lower_limit.SetValue(str(v))
        self.slider_image_stretch.SetMin(v)
        self.slider_image_stretch.SetValues(vmin, vmax)
        self.on_slider_image_stretch(None)
        if event:
            event.Skip()
    
    def on_txt_stretch_lower_lost_focus(self, event):
        self.on_txt_stretch_lower_change(event)
    
    def on_txt_stretch_upper_change(self, event):
        vmin, vmax = self.slider_image_stretch.GetValues()
        v = int(self.txt_stretch_upper_limit.GetValue())
        if v > self.stretch_max:
            v = self.stretch_max
            self.txt_stretch_upper_limit.SetValue(str(v))
        self.slider_image_stretch.SetMax(v)
        self.slider_image_stretch.SetValues(vmin, vmax)
        self.on_slider_image_stretch(None)
        if event:
            event.Skip()

    def on_txt_stretch_upper_lost_focus(self, event):
        self.on_txt_stretch_upper_change(event)

    def get_stretch_min_max(self) -> Tuple[int, int]:
        """Get current min/max from the stretch slider"""
        return self.slider_image_stretch.GetValues()
    
    def get_stretch_method(self) -> Any:
        """Get the index of the stretch method choice widget"""
        stretch_method = self.cb_image_stretch.GetCurrentSelection()
        if stretch_method == 0: # 'linear'
            stretch = LinearStretch()
        elif stretch_method == 1: # 'log'
            stretch = LogStretch()
        elif stretch_method == 2: # 'sinh'
            stretch = SinhStretch()
        elif stretch_method == 3: # 'asinh'
            stretch = AsinhStretch()
        elif stretch_method == 4: # 'square'
            stretch = SquaredStretch()
        elif stretch_method == 5: # 'sqrt'
            stretch = SqrtStretch()
        else:
            raise ValueError(f"Unknown stretch: {stretch_method}")
        return stretch
    
    def get_image_xy_flip(self) -> Tuple[bool, bool]:
        """Get if x or y axis should be flipped."""
        return (self.cb_flip_x.GetValue(), self.cb_flip_y.GetValue())
    
    def get_filters_states(self) -> dict:
        """Get the state of all the filters."""
        r = {
            'dist': (self.flt_dist.GetValue(), self.flt_dist.GetValues()),
            'B-V': (self.flt_bv.GetValue(), self.flt_bv.GetValues()),
            'B': (self.flt_b.GetValue(), self.flt_b.GetValues()),
            'V': (self.flt_v.GetValue(), self.flt_v.GetValues()),
            'R': (self.flt_r.GetValue(), self.flt_r.GetValues()),
        }
        return r
