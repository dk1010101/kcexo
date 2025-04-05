# -*- coding: UTF-8 -*-
# pylint:disable=unused-argument, invalid-name
import datetime
import astropy.units as u

import wx
import wx.propgrid

from kcexo.observatory import Observatories, Observatory
from kcexo.ui.widgets.utc_offset_validator import UTCOffsetValidator


class ObsPanel(wx.Panel):
    def __init__(self, 
                 parent,
                 wid, 
                 observatories: Observatories,
                 pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, 
                 name='observatoryPanel',
                 *argv, **kwargs):
        self.parent = parent
        
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name, *argv, **kwargs)
    
        self.utc_offset = 0.0
    
        self.observatories = observatories
        self.observatory: Observatory = None
        self.known_obs: list = []
        self.last_choice = -1
        if observatories:
            self.known_obs = list(observatories.observatories.keys())
        
        grid_sizer_obs = wx.GridBagSizer(5, 5)

        grid_sizer_obs.Add(20, 20, (0, 0), (1, 1), 0, 0)

        grid_sizer_obs.Add(20, 20, (0, 7), (1, 1), 0, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Observatory/Instrument", style=wx.ALIGN_RIGHT)
        grid_sizer_obs.Add(label_1, (1, 1), (1, 1), wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        self.cb_obs = wx.Choice(self, wx.ID_ANY, choices=self.known_obs)
        if self.known_obs:
            idx = self.known_obs.index(self.observatories.default_observatory)
            self.cb_obs.SetSelection(idx)
            self.last_choice = idx
        self.cb_obs.SetMinSize((250, 23))
        self.cb_obs.SetMaxSize((250, -1))
        grid_sizer_obs.Add(self.cb_obs, (1, 2), (1, 3), wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        self.cb_obs_show_utc = wx.CheckBox(self, wx.ID_ANY, "Show all times as UTC")
        self.cb_obs_show_utc.SetValue(1)
        grid_sizer_obs.Add(self.cb_obs_show_utc, (2, 2), (1, 3), wx.ALIGN_CENTER_VERTICAL, 0)

        self.lbl_obs_utc_offset = wx.StaticText(self, wx.ID_ANY, "UTC Offset")
        self.lbl_obs_utc_offset.Enable(False)
        grid_sizer_obs.Add(self.lbl_obs_utc_offset, (3, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)

        self.txt_obs_utc_offset = wx.TextCtrl(self, wx.ID_ANY, "", validator=UTCOffsetValidator(), style=wx.TE_PROCESS_ENTER)
        self.txt_obs_utc_offset.Enable(False)
        grid_sizer_obs.Add(self.txt_obs_utc_offset, (3, 3), (1, 1), wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        self.bt_obs_utc_reset = wx.Button(self, wx.ID_ANY, "Reset")
        self.bt_obs_utc_reset.Enable(False)
        grid_sizer_obs.Add(self.bt_obs_utc_reset, (3, 4), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)

        self.bt_select_obs = wx.Button(self, wx.ID_ANY, "Apply")
        grid_sizer_obs.Add(self.bt_select_obs, (4, 5), (1, 1), 0, 0)

        self.pgrid_obs: wx.propgrid.PropertyGridManager = wx.propgrid.PropertyGridManager(self, wx.ID_ANY)
        grid_sizer_obs.Add(self.pgrid_obs, (5, 1), (1, 6), wx.EXPAND, 0)
        grid_sizer_obs.Add(20, 20, (6, 0), (1, 1), 0, 0)
        grid_sizer_obs.Add(20, 20, (6, 7), (1, 1), 0, 0)

        grid_sizer_obs.AddGrowableRow(5)
        grid_sizer_obs.AddGrowableCol(6)

        self.SetAutoLayout(True)
        self.SetSizer(grid_sizer_obs)
        grid_sizer_obs.Fit(self)
        self.Layout()
        
        self.update_grid()
        
        self.cb_obs.Bind(wx.EVT_CHOICE, self.on_cb_obs_change)
        self.cb_obs_show_utc.Bind(wx.EVT_CHECKBOX, self.on_cb_obs_show_utc_change)
        self.bt_obs_utc_reset.Bind(wx.EVT_BUTTON, self.on_bt_obs_utc_reset)
        self.txt_obs_utc_offset.Bind(wx.EVT_TEXT_ENTER, self.on_txt_obs_utc_offset_change)
        self.txt_obs_utc_offset.Bind(wx.EVT_KILL_FOCUS, self.on_txt_obs_utc_offset_change)
    
    def set_observatories(self, obss: Observatories) -> None:
        self.observatories = obss
        self.known_obs = list(obss.observatories.keys())
        self.cb_obs.SetItems(self.known_obs)
        self.observatory = obss.observatories[obss.default_observatory]
        idx = self.known_obs.index(obss.default_observatory)
        self.cb_obs.SetSelection(idx)
        self.update_grid()
        
    def update_grid(self) -> None:
        if not self.observatories:
            return
        
        sel_obs = self.cb_obs.GetSelection()
        if sel_obs == self.last_choice:
            return
        self.last_choice = sel_obs
        self.observatory = self.observatories.observatories[self.known_obs[sel_obs]]
        obs = self.observatory
        
        self.pgrid_obs.Clear()
        page: wx.propgrid.PropertyGridPage = self.pgrid_obs.AddPage("Observatory")
        page.Append(wx.propgrid.PropertyCategory("Observatory"))
        page.Append(wx.propgrid.StringProperty("Name", wx.propgrid.PG_LABEL, self.known_obs[sel_obs]))
        page.Append(wx.propgrid.FloatProperty("Latitude (deg)", wx.propgrid.PG_LABEL, float(obs.location.lat.to(u.deg).value)))
        page.Append(wx.propgrid.FloatProperty("Longitude (deg)", wx.propgrid.PG_LABEL, float(obs.location.lon.to(u.deg).value)))
        page.Append(wx.propgrid.FloatProperty("Elevation (m)", wx.propgrid.PG_LABEL, float(obs.location.height.to(u.m).value)))
        page.Append(wx.propgrid.StringProperty("Time Zone", wx.propgrid.PG_LABEL, str(obs.observer.timezone)))
        now = datetime.datetime.now()
        self.utc_offset_hrs = obs.observer.timezone.utcoffset(now).total_seconds() / 3600.0
        self.txt_obs_utc_offset.SetValue(f"{self.utc_offset_hrs:+.1f}")
        
        page.Append(wx.propgrid.StringProperty("UTC Offset Now (hrs)", wx.propgrid.PG_LABEL, f"{self.utc_offset_hrs:+.1f}"))
        
        page.Append(wx.propgrid.PropertyCategory("Telescope & Instrument"))
        page.Append(wx.propgrid.StringProperty("Telescope Focal Length", wx.propgrid.PG_LABEL, str(obs.focal_length)))
        page.Append(wx.propgrid.StringProperty("Telescope Aperture", wx.propgrid.PG_LABEL, str(obs.aperture)))
        page.Append(wx.propgrid.StringProperty("Instrument Name", wx.propgrid.PG_LABEL, obs.sensor_name))
        page.Append(wx.propgrid.StringProperty("Instrument Size (px)", wx.propgrid.PG_LABEL, f"({str(obs.sensor_size_px[0])}, {str(obs.sensor_size_px[1])})"))
        page.Append(wx.propgrid.StringProperty("Instrument Size", wx.propgrid.PG_LABEL, f"({str(obs.sensor_size[0])}, {str(obs.sensor_size[1])})"))
        page.Append(wx.propgrid.StringProperty("Instrument Pixel Size", wx.propgrid.PG_LABEL, 
                                               f"({(obs.sensor_size[0]/obs.sensor_size_px[0]).to(u.um).value:.2f} um, {(obs.sensor_size[1]/obs.sensor_size_px[1]).to(u.um).value:.2f} um)"))
        page.Append(wx.propgrid.StringProperty("FOV", wx.propgrid.PG_LABEL, f"({obs.fov[0]}, {obs.fov[1]})"))
        
        page.Append(wx.propgrid.PropertyCategory("Configuration"))
        page.Append(wx.propgrid.FloatProperty("limiting Magnitude", wx.propgrid.PG_LABEL, obs.limiting_mag))
        page.Append(wx.propgrid.StringProperty("Exoplanet observation time before", wx.propgrid.PG_LABEL, str(obs.exo_hours_before)))
        page.Append(wx.propgrid.StringProperty("Exoplanet observation time after", wx.propgrid.PG_LABEL, str(obs.exo_hours_after)))
        page.Append(wx.propgrid.StringProperty("Meridian flip duration", wx.propgrid.PG_LABEL, str(obs.meridian_crossing_duration)))
        
    def on_cb_obs_change(self, event) -> None:
        """Deal with the change of observatory."""
        self.update_grid()

    def on_cb_obs_show_utc_change(self, event) -> None:
        """Change visibility of UTC controls depending on if we are all UTC or not."""
        val = self.cb_obs_show_utc.GetValue()
        if val:
            self.lbl_obs_utc_offset.Disable()
            self.txt_obs_utc_offset.Disable()
            self.bt_obs_utc_reset.Disable()
        else:
            self.lbl_obs_utc_offset.Enable()
            self.txt_obs_utc_offset.Enable()
            self.bt_obs_utc_reset.Enable()

    def on_bt_obs_utc_reset(self, event) -> None:
        """Reset the UTC offset text box"""
        if self.observatory:
            now = datetime.datetime.now()
            self.utc_offset_hrs = self.observatory.observer.timezone.utcoffset(now).total_seconds() / 3600.0
            self.txt_obs_utc_offset.SetValue(f"{self.utc_offset_hrs:+.1f}")
        else:
            self.txt_obs_utc_offset.SetValue("")

    def on_txt_obs_utc_offset_change(self, event) -> None:
        """Save the new UTC offset."""
        if not self.txt_obs_utc_offset.Validate():
            return
        val = self.txt_obs_utc_offset.GetValue()
        self.utc_offset_hrs = float(val)
    