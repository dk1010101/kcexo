# -*- coding: UTF-8 -*-
# pylint:disable=unused-argument, invalid-name

from astropy.table import Table

import wx
import wx.lib.newevent as NE
import wx.adv as adv


SubTransitForm, EVT_SUB_FORM = NE.NewCommandEvent()


class TransitForm(wx.Panel):
    """Representation of a value filter used to select a range of values between some min and max."""
    def __init__(self, parent, 
                 wid=wx.ID_ANY, 
                 exoclock_targets: Table=None, 
                 has_target: bool=False,
                 has_end_duration: bool=False,
                 pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, 
                 name='transitForm'):
        self.parent = parent
        self.targets: Table = exoclock_targets
        self.has_target: bool = has_target
        self.has_end_duration: bool = has_end_duration

        self.target_name = ""
        self.star_name = ""
        self.txt_target = None
        self.bt_find = None
        self.lbl_target_c = None
        self.dt_end = None
        self.txt_num_days = None
        
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name)
        
        top_sizer = wx.GridBagSizer(5, 5)
        
        #################
        ### row -/0
        row = 0
        if has_target:
            # label
            lbl_0 = wx.StaticText(self, wx.ID_ANY, "Target")
            top_sizer.Add(lbl_0, (row, 0), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
            # target name entry
            self.txt_target = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, name="txt_target")
            self.txt_target.SetSize((125, -1))
            self.txt_target.SetToolTip("ExoClock recognised target name")
            top_sizer.Add(self.txt_target, (row, 1), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
            # Find button
            self.bt_find = wx.Button(self, wx.ID_ANY, "Find")
            top_sizer.Add(self.bt_find, (row, 3), flag=wx.ALIGN_CENTRE_VERTICAL)
            # blank
            
            # coordinate
            self.lbl_target_c = wx.StaticText(self, wx.ID_ANY, "")
            self.lbl_target_c.SetSize((125,-1))
            top_sizer.Add(self.lbl_target_c, (row, 5), flag=wx.ALIGN_CENTRE_VERTICAL)
            row += 1
            
            # blank row here
            
            row += 1
        
        ### row 0/2/0
        # start date label
        name = "Start Date"
        if not self.has_end_duration:
            name = "Date"
        lbl_1 = wx.StaticText(self, wx.ID_ANY, name)
        top_sizer.Add(lbl_1, (row, 0), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
        # start date
        self.dt_start = adv.DatePickerCtrl(self, wx.ID_ADD)
        top_sizer.Add(self.dt_start, (row, 1), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
        if self.has_end_duration:
            # end date label
            lbl_2 = wx.StaticText(self, wx.ID_ANY, "End Date")
            top_sizer.Add(lbl_2, (row, 3), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
            # end date control
            self.dt_end = adv.DatePickerCtrl(self, wx.ID_ADD)
            top_sizer.Add(self.dt_end, (row, 5), flag=wx.ALIGN_CENTRE_VERTICAL)
            row += 1
            ### row -/3/1
            lbl_3 = wx.StaticText(self, wx.ID_ANY, "Num Days")
            top_sizer.Add(lbl_3, (row, 0), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
            self.txt_num_days = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, name="txt_num_days")
            self.txt_target.SetSize((125, -1))
            top_sizer.Add(self.txt_num_days, (row, 1), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
            row += 1
        
        ### row 1/4/2
        # blank
        row += 1
        
        ### row 2/5/3 - Filters
        lbl_4 = wx.StaticText(self, wx.ID_ANY, "Filters")
        top_sizer.Add(lbl_4, (row, 0), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
        row += 1
        
        ### row 3/6/4 - Use Horizon
        self.cb_horizon = wx.CheckBox(self, wx.ID_ANY, "Use Horizon")
        self.cb_horizon.SetValue(True)
        top_sizer.Add(self.cb_horizon, (row, 1), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
        row += 1

        ### row 4/7/5 - Twilight
        lbl_5 = wx.StaticText(self, wx.ID_ANY, "Use Twilight")
        top_sizer.Add(lbl_5, (row, 1), flag=wx.ALIGN_CENTRE_VERTICAL)
        self.ch_twilight = wx.Choice(self, wx.ID_ANY, name="ch_twilight",
                                     choices=["Astronomical", "Nautical", "Civil", "None"])
        top_sizer.Add(self.ch_twilight, (row, 2), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
        row += 1
        
        ### row 5/8/5 - Allow flip
        self.cb_allow_flip = wx.CheckBox(self, wx.ID_ANY, "Allow meridian flip")
        self.cb_hocb_allow_fliprizon.SetValue(True)
        top_sizer.Add(self.cb_allow_flip, (row, 1), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL)
        row += 1

        ### row 6/9/6 - Apply
        self.bt_apply = wx.Button(self, wx.ID_ANY, "Apply")
        top_sizer.Add(self.bt_apply, (row, 5), flag=wx.ALIGN_CENTRE_VERTICAL)
        
        ###############
        # no growable col/row
        
        ###############
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        top_sizer.Fit(self)
        self.Layout()
        
        ###############
        # events
        if self.has_target:
            self.bt_find.Bind(wx.EVT_BUTTON, self.on_bt_find)
        
        if self.has_end_duration:
            self.txt_num_days.Bind(wx.EVT_TEXT_ENTER, self.on_txt_num_days_change)
            self.txt_num_days.Bind(wx.EVT_KILL_FOCUS, self.on_txt_num_days_change)
            self.dt_start.Bind(adv.EVT_DATE_CHANGED, self.on_dt_start_change)
            self.dt_end.Bind(adv.EVT_DATE_CHANGED, self.on_dt_end_change)
        
        self.bt_apply.Bind(wx.EVT_BUTTON, self.on_bt_apply)
        
    def on_bt_find(self, event):
        """Find a target, store the name and get the coordinates"""
        t = self.targets[self.targets['name'] == self.txt_target.GetValue()]
        if len(t):
            self.target_name = t['name']
            self.star_name = t['star']
            c_ra = t['ra_j2000']
            c_dec = t['dec_j2000']
            self.lbl_target_c.SetLabel(c_ra[:11]+" "+c_dec[:12])
        else:
            self.target_name = ""
            self.star_name = ""
            wx.MessageBox("Target not found! Please try again.", "Not found...", style=wx.OK|wx.ICON_EXCLAMATION)
        
    def on_txt_num_days_change(self, event):
        """Make sure that start, end and num days are all in sync"""
        print("Not implemented")
        
    def on_dt_start_change(self, event):
        """Make sure that start, end and num days are all in sync"""
        print("Not implemented")
        
    def on_dt_end_change(self, event):
        """Make sure that start, end and num days are all in sync"""
        print("Not implemented")
        
    def on_bt_apply_find(self, event):
        """Submit the form"""
        wx.PostEvent(self.parent, SubTransitForm(wx.ID_ANY))
