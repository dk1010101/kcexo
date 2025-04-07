# -*- coding: UTF-8 -*-
# cspell:ignore exoclock
# pylint:disable=unused-argument, invalid-name

from functools import partial
from typing import List, Dict, Any

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import astropy.units as u
from astropy.table import Table
from astropy.time import Time

import wx

from kcexo.transit import Transit
from kcexo.planet import Planet
from kcexo.observatory import Observatory
from kcexo.data.exoclock_data import ExoClockData
from kcexo.viz.transit import create_sky_transit, create_transit_horizon_plot, create_transit_schematic
from kcexo.viz.render import render_to_png
from kcexo.ui.widgets.sortable_grid import SortableGrid, GridData, col_fmt_float, col_fmt_length, col_fmt_timeonly, col_fmt_str, PlotCellRenderer, col_fmt_length_as_f, col_fmt_quantity_as_f
from kcexo.ui.planner.transit_form import TransitForm, EVT_SUB_FORM



class MultipleTargetsPanel(wx.Panel):
    
    TITLE = "Multiple Targets"
    
    def __init__(self, 
                 parent,
                 wid, 
                 observatory: Observatory,
                 exoclock_db: ExoClockData,
                 *argv, 
                 pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, 
                 name='observatoryPanel',
                 **kwargs):
        
        matplotlib.use('Agg')
        
        self.parent = parent
        self.obs: Observatory = observatory
        self.db: ExoClockData = exoclock_db
        
        self.utc_offset_hours = 0.0
        
        # filtering data
        self._start_date: Time = Time.now()
        self._end_date: Time = Time.now()
        self.must_refresh: bool = True
        self.transits: Dict[str, Transit]
        self.filtered_transits: Dict[str, Transit]
        self.visible: List[str] = []
        
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name, *argv, **kwargs)
        
        ##############################
        main_sizer = wx.GridBagSizer(5, 5)
        
        ###############
        # row 0
        main_sizer.Add(20, 20, (0, 0), (1, 1), 0, 0)
        main_sizer.Add(20, 20, (0, 3), (1, 1), 0, 0)

        self.lbl_title = wx.StaticText(self, wx.ID_ANY, self.TITLE)
        self.lbl_title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))

        main_sizer.Add(self.lbl_title, (0, 1), (1, 2), 0, 0)
        
        ###############
        # row 2
        self.filter = TransitForm(self, wx.ID_ANY, self.db, False, True)
        main_sizer.Add(self.filter, (1, 1), (1, 1), wx.EXPAND, 0)
        
        ###############
        # row 3
        self.grid = SortableGrid(self, wx.ID_ANY)
        main_sizer.Add(self.grid, (2, 1), (1, 2), wx.EXPAND, 0)
        
        ###############
        # row 4
        main_sizer.Add(20, 20, (3, 0), (1, 1), 0, 0)
        main_sizer.Add(20, 20, (3, 3), (1, 1), 0, 0)

        ##############################
        main_sizer.AddGrowableRow(2)
        main_sizer.AddGrowableCol(2)

        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()
        
        self.filter.Bind(EVT_SUB_FORM, self.on_filter_form_sub)
    
    def set_observatory(self, obs: Observatory) -> None:
        """Set observatory ot the new value"""
        if obs == self.obs:
            return
        
        self.obs = obs
        self.lbl_title.SetLabel(f"{self.TITLE} - {self.obs.name}")
        self._start_date = None
        self._end_date = None
        self.on_filter_form_sub(None)
        
    def set_utc_offset(self, utc_offset_hours: float) -> None:
        """Set utc offset"""
        self.utc_offset_hours = utc_offset_hours
        
    def set_db(self, db: ExceptionGroup) -> None:
        """Change the exoclock db we are using."""
        self.db = db
        self.filter.set_db(self.db)
        
    def on_filter_form_sub(self, event: wx.Event) -> None:
        """Handle filter form submission"""
        if not self.obs:
            return
        start_date, end_date, target_name, use_horizon, allow_flip, twilight = self.filter.get_values()
        if start_date != self._start_date or end_date != self._end_date or self.must_refresh:
            self._start_date = start_date
            self._end_date = end_date
            self.transits = self.db.get_transits(start_date, end_date, self.obs, True, True)
            
        if target_name:
            self.filtered_transits, self.visible = self.db.filter_transits({target_name: self.transits[target_name]}, self.obs, use_horizon, twilight.lower(), allow_flip, allow_flip)
        else:
            self.filtered_transits, self.visible = self.db.filter_transits(self.transits, self.obs, use_horizon, twilight.lower(), allow_flip, allow_flip)
        self.update_grid()
    
    def update_grid(self) -> None:
        """Update the grid with the transits in the `filtered transits` variable"""
        
        col_names = ["Target", "Priority", "Obs (Recent)", 'Min Aper (")', "Mag R", "Mag V", "Depth R", "Duration (hr)", "Pre", "Start", "End", "Post", "GRAPH_Transit"]
        col_width = [20*5, 13*5, 18*5, 18*5, 12*5, 12*5, 12*5, 17*5, 13*5, 13*5, 13*5, 13*5, 300]
        col_formatting = [col_fmt_str, col_fmt_str, col_fmt_str, partial(col_fmt_length_as_f,target_unit=u.imperial.inch), col_fmt_str, col_fmt_str, col_fmt_quantity_as_f, col_fmt_quantity_as_f, col_fmt_timeonly, col_fmt_timeonly, col_fmt_timeonly, col_fmt_timeonly, PlotCellRenderer]
        data: List[List[Any]] = []
        
        for name, transits in self.filtered_transits.items():
            wx.Yield() # ?
            planet: Planet = self.db.data[name]
            for transit in transits:
                plot_data: bytes = self.create_plot(planet, transit)
                row = [
                    planet.name,
                    planet.status.priority,
                    f"{planet.status.total_observations} ({planet.status.total_observations_recent})",
                    planet.status.min_aperture,
                    planet.host_star.mag.get("R", np.nan),
                    planet.host_star.mag.get("V", np.nan),
                    planet.depth,
                    planet.duration,
                    transit.pre_ingress,
                    transit.ingress,
                    transit.egress,
                    transit.post_egress,
                    plot_data
                ]
                data.append(row)
        
        gd = GridData(data=data, col_widths=col_width, col_names=col_names, col_formatting=col_formatting, col_graph_prefix="GRAPH_")
        self.grid.set_data(gd)
    
    def create_plot(self, planet: Planet, transit: Transit) -> bytes:
        """Create transit plot"""
        fig = plt.figure()
        fig.set_size_inches(6, 5)
        gs = fig.add_gridspec(2, 2)
        top_left = fig.add_subplot(gs[0, 0])
        bottom_left = fig.add_subplot(gs[1, 0])
        right = fig.add_subplot(gs[0:2, 1], projection='polar')
        create_transit_schematic(transit, self.obs.meridian_crossing_duration, planet.name, fig=fig, ax=top_left)
        create_transit_horizon_plot(transit, planet, self.obs, fig=fig, ax=bottom_left)
        create_sky_transit(transit, planet, self.obs, fig=fig, ax=right)
        fig.tight_layout()
        buf = render_to_png(fig)
        return buf
    