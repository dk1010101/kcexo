import wx

from kcexo.ui.widgets.range_slider import RangeSlider
from kcexo.ui.widgets.filter_control import ValFilter
from kcexo.ui.widgets.mpl_canvas import MatplotlibPanel

# TODO: create new events so that we don't have to bind to everything

class TopPanel(wx.Panel):
    """Top pane panel for the comparator star tool"""
    def __init__(self, parent, id=wx.ID_ANY, 
                 background_colour: wx.Colour=wx.WHITE, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 name='topPanel'):
        super().__init__(parent=parent, id=id, pos=pos, size=size, name=name)
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
        self.figure = self.canvas_panel.plt.figure
        self.canvas = self.canvas_panel.plt
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
        
        panel = wx.Panel(parent, -1)
        panel.SetBackgroundColour(bg_col)
        
        panel_sizer = wx.FlexGridSizer(1, 15, 0, 0)
        
        panel_sizer.Add((15, 15), 0, 0, 0)
        label_13 = wx.StaticText(panel, wx.ID_ANY, "Image Stretch ", style=wx.ALIGN_RIGHT)
        panel_sizer.Add(label_13, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        panel_sizer.Add((10, 15), 0, 0, 0)

        self.cb_image_stretch = wx.ComboBox(panel, wx.ID_ANY, choices=["linear", "log", "sinh", "asinh", "square", "sqrt"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SIMPLE)
        self.cb_image_stretch.SetMinSize((110, 15))
        self.cb_image_stretch.SetSelection(2)
        panel_sizer.Add(self.cb_image_stretch, 0, wx.EXPAND, 0)

        panel_sizer.Add((20, 15), 0, 0, 0)

        self.lbl_image_stretch_min = wx.StaticText(panel, wx.ID_ANY, "        ", style=wx.ALIGN_RIGHT)
        panel_sizer.Add(self.lbl_image_stretch_min, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        self.slider_image_stretch = RangeSlider(panel, lowValue=0, highValue=65535, minValue=0, maxValue=65535)
        self.slider_image_stretch.SetBackgroundColour(bg_col)
        self.slider_image_stretch.SetMinSize((300, 15))
        panel_sizer.Add(self.slider_image_stretch, 0, wx.EXPAND, 0)

        self.lbl_image_stretch_max = wx.StaticText(panel, wx.ID_ANY, "        ", style=wx.ALIGN_LEFT)
        panel_sizer.Add(self.lbl_image_stretch_max, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        panel_sizer.Add((20, 15), 0, 0, 0)

        self.bt_image_stretch_apply = wx.Button(panel, wx.ID_ANY, "Apply")
        panel_sizer.Add(self.bt_image_stretch_apply, 0, 0, 0)
        self.bt_image_stretch_reset = wx.Button(panel, wx.ID_ANY, "Reset")
        panel_sizer.Add(self.bt_image_stretch_reset, 0, 0, 0)

        panel_sizer.Add((40, 15), 0, 0, 0)

        self.cb_flip_x = wx.CheckBox(panel, wx.ID_ANY, "Flip X")
        panel_sizer.Add(self.cb_flip_x, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        self.cb_flip_y = wx.CheckBox(panel, wx.ID_ANY, "Flip Y")
        panel_sizer.Add(self.cb_flip_y, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        self.bt_image_reset = wx.Button(panel, wx.ID_ANY, "Reset Zoom")
        panel_sizer.Add(self.bt_image_reset, 0, 0, 0)
        
        ########
        # events
        # self.slider_image_stretch.Bind(wx.EVT_LEFT_UP, self.on_slider_image_stretch)
        # self.bt_image_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        # self.bt_image_stretch_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_reset)
        # self.bt_image_stretch_apply.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        # self.cb_flip_x.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        # self.cb_flip_y.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        
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
        # self.flt_dist.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        # self.flt_bv.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        # self.flt_b.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        # self.flt_v.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        # self.flt_r.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        
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
        self.flt_dist.SetTargetValue(target_vals['dist'])
        self.flt_bv.SetTargetValue(target_vals['B-V'])
        self.flt_b.SetTargetValue(target_vals['B'])
        self.flt_v.SetTargetValue(target_vals['V'])
        self.flt_r.SetTargetValue(target_vals['R'])
    
    def set_filter_minmax(self, minmax_vals: dict) -> None:
        self.flt_dist.SetMinMax(*minmax_vals['dist'])
        self.flt_bv.SetMinMax(*minmax_vals['B-V'])
        self.flt_b.SetMinMax(*minmax_vals['B'])
        self.flt_v.SetMinMax(*minmax_vals['V'])
        self.flt_r.SetMinMax(*minmax_vals['R'])
