# -*- coding: UTF-8 -*-

import wx

from kcexo.planet import Planet
from kcexo.star import Star


class PlanetDetails(wx.Panel):
    def __init__(self, parent, wid=wx.ID_ANY,
                 planet: Planet=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 name='planetDetails'):
        self.planet = planet
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name)
        
        title_font = wx.Font(wx.FONTSIZE_MEDIUM, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, "Segoe UI")
        
        main_sizer = wx.GridBagSizer(5, 5)
        
        self.lbl_name = wx.StaticText(self, wx.ID_ANY, "Planet Name")
        self.lbl_host_star = wx.StaticText(self, wx.ID_ANY, "Host Star")
        self.lbl_ephem_mid_time = wx.StaticText(self, wx.ID_ANY, "Ephemeris Mid Time")
        self.lbl_period = wx.StaticText(self, wx.ID_ANY, "Ephemeris Period")
        self.lbl_depth = wx.StaticText(self, wx.ID_ANY, "Transit Depth")
        self.lbl_duration = wx.StaticText(self, wx.ID_ANY, "Transit Duration")
        self.lbl_RpRs = wx.StaticText(self, wx.ID_ANY, "Rp/Rs")
        self.lbl_aRs = wx.StaticText(self, wx.ID_ANY, "a/Rs")
        self.lbl_i = wx.StaticText(self, wx.ID_ANY, "i")
        self.lbl_e = wx.StaticText(self, wx.ID_ANY, "e")
        self.lbl_omega = wx.StaticText(self, wx.ID_ANY, "omega")
        self.lbl_status = wx.StaticText(self, wx.ID_ANY, "Status")
        self.lbl_status_priority = wx.StaticText(self, wx.ID_ANY, "Priority")
        self.lbl_status_min_aperture = wx.StaticText(self, wx.ID_ANY, "Min Aperture")
        self.lbl_status_ec_observations = wx.StaticText(self, wx.ID_ANY, "ExoClock Observations (recent)")
        self.lbl_status_total_observations = wx.StaticText(self, wx.ID_ANY, "Total Observations (recent)")
        self.lbl_oc = wx.StaticText(self, wx.ID_ANY, "O-C")
        