# -*- coding: UTF-8 -*-
# cspell:ignore exoclock KCEXO
# pylint:disable=unused-argument, invalid-name
import logging
from functools import partial
from typing import List, Dict, Any, Tuple

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from pubsub import pub

import astropy.units as u
from astropy.time import Time

import wx

from kcexo.transit import Transit
from kcexo.planet import Planet
from kcexo.observatory import Observatory
from kcexo.data.exoclock_data import ExoClockData
from kcexo.viz.transit import create_sky_transit, create_transit_horizon_plot, create_transit_schematic
from kcexo.viz.render import render_to_png, close_figure
from kcexo.ui.widgets.sortable_grid import SortableGrid, GridData, col_fmt_str, PlotCellRenderer, col_fmt_length_as_f, col_fmt_quantity_as_f, col_fmt_datetime
from kcexo.ui.planner.transit_form import TransitForm, EVT_SUB_FORM
from kcexo.ui.planner.utils import prevent_tab_changes, update_status


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
        self.log = logging.getLogger("KCEXO")
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
        
        ##############################

        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()
        
        self.filter.Bind(EVT_SUB_FORM, self.on_filter_form_sub)
        
        pub.subscribe(self.on_pubsub_observatory_change, "observatory.change")
        pub.subscribe(self.on_pubsub_utcoffset_change, "utcoffset.change")
    
    def set_observatory(self, obs: Observatory) -> None:
        """Set observatory ot the new value"""
        self.log.debug("MTP - set_observatory '%s'", obs.name if obs else 'None')
        
        if obs == self.obs:
            return
        
        self.obs = obs
        self.lbl_title.SetLabel(f"{self.TITLE} - {self.obs.name}")
        self._start_date = None
        self._end_date = None
        self.on_filter_form_sub(None)
        
    def set_utc_offset(self, utc_offset_hours: float) -> None:
        """Set utc offset"""
        self.log.debug("MTP - set_utc_offset: %f", utc_offset_hours)
        self.utc_offset_hours = utc_offset_hours
        
    def set_db(self, db: ExceptionGroup) -> None:
        """Change the exoclock db we are using."""
        self.log.debug("MTP - set_db")
        self.db = db
        self.filter.set_db(self.db)
    
    def on_pubsub_observatory_change(self, data) -> None:
        """Handel pubsub observatory change"""
        self.set_observatory(data)
        
    def on_pubsub_utcoffset_change(self, data) -> None:
        """Handle pubsub utc offset change"""
        self.set_utc_offset(data)
        self.update_grid()
    
    def on_filter_form_sub(self, event: wx.Event) -> None:
        """Handle filter form submission"""
        self.log.debug("MTP - on_filter_form_sub")
        if not self.obs:
            return
        with prevent_tab_changes():
            start_date, end_date, target_name, use_horizon, allow_flip, twilight = self.filter.get_values()
            if start_date != self._start_date or end_date != self._end_date or self.must_refresh:
                self._start_date = start_date
                self._end_date = end_date
                with update_status("Searching for transits..."):
                    self.transits = self.db.get_transits(start_date, end_date, self.obs, True, True)
                
            with update_status("Filtering transits..."):
                if target_name:
                    self.filtered_transits, self.visible = self.db.filter_transits({target_name: self.transits[target_name]}, self.obs, use_horizon, twilight.lower(), allow_flip, allow_flip)
                else:
                    self.filtered_transits, self.visible = self.db.filter_transits(self.transits, self.obs, use_horizon, twilight.lower(), allow_flip, allow_flip)
                self.update_grid()
    
    def update_grid(self) -> None:
        """Update the grid with the transits in the `filtered transits` variable"""
        self.log.debug("STP - update_grid")
        with prevent_tab_changes("Updating All Targets transit list..."):
        
            col_names = ["Target", "Priority", "# Obs", "# Recent", 'Min Aper (")', "Mag R", "Mag V", "Depth R", "Duration (hr)", "Pre", "Start", "End", "Post", "GRAPH_Transit Profile", "GRAPH_Horizon Transit", "GRAPH_Sky Transit"]
            col_width = [20*5, 13*5, 18*5, 18*5, 18*5, 12*5, 12*5, 12*5, 17*5, 13*5, 13*5, 13*5, 13*5, 200, 200, 200]
            datetime_renderer = partial(col_fmt_datetime, utc_offset_hours=self.utc_offset_hours)
            col_formatting = [col_fmt_str, col_fmt_str, col_fmt_str, col_fmt_str, partial(col_fmt_length_as_f,target_unit=u.imperial.inch), col_fmt_str, col_fmt_str, col_fmt_quantity_as_f, col_fmt_quantity_as_f, datetime_renderer, datetime_renderer, datetime_renderer, datetime_renderer, PlotCellRenderer, PlotCellRenderer, PlotCellRenderer]
            data: List[List[Any]] = []
            
            for name, transits in self.filtered_transits.items():
                wx.Yield() # ?
                planet: Planet = self.db.data[name]
                for transit in transits:
                    plot_data_1, plot_data_2, plot_data_3 = self.create_plots(planet, transit)
                    row = [
                        planet.name,
                        planet.status.priority,
                        planet.status.total_observations,
                        planet.status.total_observations_recent,
                        planet.status.min_aperture,
                        planet.host_star.mag.get("R", np.nan),
                        planet.host_star.mag.get("V", np.nan),
                        planet.depth,
                        planet.duration,
                        transit.pre_ingress,
                        transit.ingress,
                        transit.egress,
                        transit.post_egress,
                        plot_data_1, plot_data_2, plot_data_3
                    ]
                    data.append(row)
            
            gd = GridData(data=data, col_widths=col_width, col_names=col_names, col_formatting=col_formatting, col_graph_prefix="GRAPH_", row_height=150)
            self.grid.set_data(gd)
    
    def create_plots(self, planet: Planet, transit: Transit) -> Tuple[bytes, bytes, bytes]:
        """Create transit plot"""
        fig = plt.figure()
        dpi = 50
        size = (200, 150)
        
        fig.set_dpi(dpi)
        fig.set_size_inches(size[0]/dpi, size[1]/dpi)
        ax = fig.add_subplot(1, 1, 1)
        create_transit_schematic(transit, self.obs.meridian_crossing_duration, planet.name, fig=fig, ax=ax)
        fig.tight_layout()
        buf1 = render_to_png(fig, clear_fig=False)
        fig.clf()
        
        ax = fig.add_subplot(1, 1, 1)
        create_transit_horizon_plot(transit, planet, self.obs, fig=fig, ax=ax)
        fig.tight_layout()
        buf2 = render_to_png(fig, clear_fig=False)
        fig.clf()
        
        ax = fig.add_subplot(1, 1, 1, projection="polar")
        create_sky_transit(transit, planet, self.obs, fig=fig, ax=ax)
        fig.tight_layout()
        buf3 = render_to_png(fig, clear_fig=False)
                
        close_figure(fig)
        
        return (buf1, size), (buf2, size), (buf3, size)
    