# -*- coding: UTF-8 -*-
# pylint:disable=unused-argument, invalid-name

import astropy.units as u
from astropy.table import Table

import wx


from kcexo.observatory import Observatory, Observatories
from kcexo.data.exoclock_data import ExoClockData
from kcexo.ui.widgets.sortable_grid import SortableGrid
from kcexo.ui.planner.transit_form import TransitForm, EVT_SUB_FORM



class SingleTargetPanel(wx.Panel):
    
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
        self.parent = parent
        self.obs: Observatory = observatory
        self.db: ExoClockData = exoclock_db
        self.utc_offset_hours: float = 0.0
        
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name, *argv, **kwargs)
        
        ##############################
        main_sizer = wx.GridBagSizer(5, 5)
        
        ###############
        # row 0
        main_sizer.Add(20, 20, (0, 0), (1, 1), 0, 0)
        main_sizer.Add(20, 20, (0, 3), (1, 1), 0, 0)

        lbl = wx.StaticText(self, wx.ID_ANY, "Single Target over Time")
        lbl.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))

        main_sizer.Add(lbl, (0, 1), (1, 2), 0, 0)
        
        ###############
        # row 2
        self.filter = TransitForm(self, wx.ID_ANY, self.db, True, True)
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
        
    def set_db(self, db: ExceptionGroup) -> None:
        """Change the exoclock db we are using."""
        self.db = db
        self.filter.set_db(self.db)

    def set_observatory(self, obs: Observatory) -> None:
        """Set observatory ot the new value"""
        self.obs = obs
        
    def set_utc_offset(self, utc_offset_hours: float) -> None:
        """Set utc offset"""
        self.utc_offset_hours = utc_offset_hours
    
    def on_filter_form_sub(self, event) -> None:
        print("on_filter_form_sub not implemented")
        event.Skip()
