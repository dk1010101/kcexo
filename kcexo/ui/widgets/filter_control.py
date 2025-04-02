# -*- coding: UTF-8 -*-
# pylint:disable=unused-argument, invalid-name

import numpy as np

import wx

from .range_slider import RangeSlider


class ValFilter(wx.Panel):
    """Representation of a value filter used to select a range of values between some min and max."""
    def __init__(self, parent, 
                 wid=wx.ID_ANY, 
                 title: str="", 
                 target_value: float=0.0,
                 min_val: float=0.0,
                 max_val: float=1.0,
                 has_nan: bool=True,
                 num_precision: int=2,
                 show_titles: bool=False,
                 titles: list|None=None,
                 title_font_size: int|None = None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 colour=wx.WHITE,
                 name='filterPanel'):
        self.parent = parent
        self.num_precision: int = num_precision
        self.has_nan: bool = has_nan
        
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name)
        
        top_sizer = wx.GridBagSizer(5, 5)
        
        start_row = 0
        #################
        ### row 0 - title
        if show_titles:
            if titles is None:
                raise ValueError("Can't have and have not titles. Like doh!")
            
            if title_font_size is None:
                sz = 7
            else:
                sz = title_font_size
            font = wx.Font(sz, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            
            ### row 0
            lbl_1 = wx.StaticText(self, wx.ID_ANY, titles[0])
            lbl_1.SetFont(font)
            lbl_2 = wx.StaticText(self, wx.ID_ANY, titles[1])
            lbl_2.SetFont(font)
            lbl_3 = wx.StaticText(self, wx.ID_ANY, titles[2])
            lbl_3.SetFont(font)
            top_sizer.Add(lbl_1, (0, 1), flag=wx.ALIGN_CENTER)
            top_sizer.Add(lbl_2, (0, 2), flag=wx.ALIGN_CENTER)
            top_sizer.Add(lbl_3, (0, 4), flag=wx.ALIGN_CENTER)
            start_row = 1            

        ### row 1 - title
        label_title = wx.StaticText(self, wx.ID_ANY, title)
        top_sizer.Add(label_title, (start_row, 1), (1, 4), flag=wx.EXPAND)

        ### row 2 - use / slider / nan
        top_sizer.Add((3,0), (start_row+1, 0), flag=wx.EXPAND)
        self.lbl_target_value = wx.StaticText(self, wx.ID_ANY, f"{target_value:.{self.num_precision}f}")
        top_sizer.Add(self.lbl_target_value, (start_row+1, 1), flag=wx.ALIGN_CENTER)
        self.cb_use = wx.CheckBox(self, wx.ID_ANY, "", name=self.GetName()+"_cb_use")
        top_sizer.Add(self.cb_use, (start_row+1, 2), flag=wx.ALIGN_CENTER)
        self.slider = RangeSlider(self, lowValue=0, highValue=10, minValue=0, maxValue=10, name=self.GetName()+"_slider")
        self.slider.SetBackgroundColour(colour)
        top_sizer.Add(self.slider, (start_row+1, 3), flag=wx.EXPAND)
        self.cb_nan = wx.CheckBox(self, wx.ID_ANY, "", name=self.GetName()+"_cb_nan")
        top_sizer.Add(self.cb_nan, (start_row+1, 4), flag=wx.ALIGN_CENTER)
        if not self.has_nan:
            self.cb_nan.Disable()
        
        ### row 2 - min/max
        top_sizer.Add((3,0), (start_row+2, 0), flag=wx.EXPAND)
        top_sizer.Add((30,0), (start_row+2, 1), flag=wx.EXPAND)
        top_sizer.Add((25,0), (start_row+2, 2), flag=wx.EXPAND)
        grid_sizer_mm = wx.GridSizer(1, 2, 0, 0)
        top_sizer.Add(grid_sizer_mm, (start_row+2, 3), flag=wx.EXPAND)
        self.lbl_min = wx.StaticText(self, wx.ID_ANY, str(min_val))
        grid_sizer_mm.Add(self.lbl_min, 0, 0, 0)
        self.lbl_max = wx.StaticText(self, wx.ID_ANY, str(max_val))
        grid_sizer_mm.Add(self.lbl_max, 0, wx.ALIGN_RIGHT, 0)
        top_sizer.Add((25,0), (start_row+2, 4), flag=wx.EXPAND)
        
        top_sizer.AddGrowableCol(3)
        
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        top_sizer.Fit(self)
        self.Layout()
        
        if self.has_nan:
            self.cb_nan.Bind(wx.EVT_CHECKBOX, self.on_cb_nan)
        self.cb_use.Bind(wx.EVT_CHECKBOX, self.on_cb_val)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
    
    def on_cb_nan(self, event):
        """Process use-NaNs check box."""
        if self.cb_use.GetValue():
            self.post_checkbox_event()
            
    def on_cb_val(self, event):
        """Process Use check box."""
        self.post_checkbox_event()
        
    def on_slider_change(self, event):
        """Process slider handles movements."""
        low, high = self.slider.GetValues()
        self.lbl_min.SetLabel(f"{low:.{self.num_precision}f}")
        self.lbl_max.SetLabel(f"{high:.{self.num_precision}f}")
        if self.cb_use.GetValue():
            self.post_checkbox_event()
        
    def Enable(self, enable=True):
        """Enable all controls."""
        super().Enable(enable)
        self.Refresh()

    def Disable(self):
        """Disable all controls."""
        super().Disable()
        self.Refresh()
        
    def post_checkbox_event(self):
        """Send the event that the culter has changed."""
        event = wx.PyCommandEvent(wx.EVT_CHECKBOX.typeId, self.parent.GetId())
        event.SetEventObject(self.parent)
        #wx.PostEvent(self.parent.GetEventHandler(), event)
        self.GetEventHandler().ProcessEvent(event)

    def GetValue(self):
        """Return is this control is to be used to create filters."""
        return self.cb_use.GetValue()

    def GetValues(self):
        """Return slider values as well as the state of Use-NaNs check box."""
        return *self.slider.GetValues(), self.cb_nan.GetValue() if self.has_nan else False
    
    def SetMinMax(self, v_min: float, v_max: float, precision=None):
        """Set the slider min-max extent."""
        if v_min is None or np.isnan(v_min) or np.ma.is_masked(v_min) or v_max is None or np.isnan(v_max) or np.ma.is_masked(v_max):
            self.Disable()
        else:
            self.Enable()
            
        if precision is None:
            p = self.num_precision
        else:
            p = precision
        if (v_min or v_min == 0) and not (np.isnan(v_min) or np.ma.is_masked(v_min)):
            self.lbl_min.SetLabel(f"{v_min:.{p}f}")
        else:
            self.lbl_min.SetLabel("--")
        if (v_max or v_max == 0) and not (np.isnan(v_max) or np.ma.is_masked(v_max)):
            self.lbl_max.SetLabel(f"{v_max:.{p}f}")
        else:
            self.lbl_max.SetLabel("--")
        self.slider.ResetMinMax(v_min, v_max)
    
    def SetCBVal(self, val):
        """Set Use state."""
        self.cb_use.SetValue(val)
        
    def SetCBNaNVal(self, val):
        """Set Use-NaNs state."""
        if self.cb_nan is not None:
            self.cb_nan.SetValue(val)

    def SetTargetValue(self, val, precision=None):
        """Set the target's value on the control so that users can easily see what they are working with."""
        if val is None or np.isnan(val) or np.ma.is_masked(val):
            cmin = self.slider.GetMin()
            cmax = self.slider.GetMax()
            if cmin is None or np.isnan(cmin) or cmax is None or np.isnan(cmax):
                self.Disable()
        else:
            self.Enable()
        if precision is None:
            p = self.num_precision
        else:
            p = precision
        if (val or val==0) and not np.isnan(val) and not np.ma.is_masked(val):
            self.lbl_target_value.SetLabel(f"{val:.{p}f}")
        else:
            self.lbl_target_value.SetLabel("--")

    def reset(self) -> None:
        """Clear the widget and reset to initial state."""
        self.cb_use.SetValue(False)
        self.cb_nan.SetValue(False)
        self.SetMinMax(0, 1)
        self.SetTargetValue(np.nan)
