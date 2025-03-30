# -*- coding: UTF-8 -*-
# cSpell:ignore hmsdms
from typing import Any

import wx

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table


class GridPanel(wx.Panel):
    """Bottom pane panel for the data grid"""
    def __init__(self, parent, id=wx.ID_ANY, 
                 background_colour: wx.Colour=wx.WHITE, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 name='topPanel'):
        super().__init__(parent=parent, id=id, pos=pos, size=size, name=name)
        self.data: Table
        
        self.controls_collection = []
        self.background_colour = background_colour

        self.grid_data = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_data.CreateGrid(20, 13)
        self.grid_data.SetColLabelValue(0, "Name")
        self.grid_data.SetColLabelValue(1, "oid")
        self.grid_data.SetColLabelValue(2, "RA")
        self.grid_data.SetColLabelValue(3, "DEC")
        self.grid_data.SetColLabelValue(4, "Type")
        self.grid_data.SetColLabelValue(5, "Var Type")
        self.grid_data.SetColLabelValue(6, "Distance")
        self.grid_data.SetColLabelValue(7, "B-V")
        self.grid_data.SetColLabelValue(8, "B")
        self.grid_data.SetColLabelValue(9, "V")
        self.grid_data.SetColLabelValue(10, "R")
        self.grid_data.SetColLabelValue(11, "Gaia ID")
        self.grid_data.SetColLabelValue(12, "TIC")
        
        self.grid_data.SetColSize(0, 23*5)
        self.grid_data.SetColSize(1, 11*5)
        self.grid_data.SetColSize(2, 17*5)
        self.grid_data.SetColSize(3, 18*5)
        self.grid_data.SetColSize(4, 8*5)
        self.grid_data.SetColSize(5, 11*5)
        self.grid_data.SetColSize(6, 11*5)
        self.grid_data.SetColSize(7, 9*5)
        self.grid_data.SetColSize(8, 9*5)
        self.grid_data.SetColSize(9, 9*5)
        self.grid_data.SetColSize(10, 9*5)
        self.grid_data.SetColSize(11, 34*5)
        self.grid_data.SetColSize(12, 20*5)
        
        self.grid_data.EnableEditing(0)
        self.grid_data.SetSelectionMode(wx.grid.Grid.SelectRows)
        ############################################
        sizer = wx.FlexGridSizer(1, 1, 0, 0)
        sizer.Add(self.grid_data, 0, wx.EXPAND | wx.TOP, 1)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        ############################################
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        
        ########
        # events
        # self.grid_data.Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL, self.on_grid_data_select)
    
    def resize_grid(self) -> None:
        """Resize the grid to match the data that we have."""
        current, new = (self.grid_data.GetNumberRows(), len(self.data))
        if new < current:
            self.grid_data.DeleteRows(0, current-new, True)
        if new > current:
            self.grid_data.AppendRows(new-current)
    
    def update_grid(self, new_data: Table) -> None:
        
        self.data = new_data
        
        def fmtflt(v: Any, precision: int=2) -> str:
            if v or v == 0.0:
                return f"{v:.{precision}f}"
            else:
                return "--"
            
        self.resize_grid()
        for row_idx, row in enumerate(self.data.iterrows()):
            self.grid_data.SelectRow(row_idx, True)
            self.grid_data.ClearSelection()

            self.grid_data.SetCellValue(row_idx, 0, row[0])
            self.grid_data.SetCellValue(row_idx, 1, str(row[1]))
            c = SkyCoord(ra=float(row[2])*u.hourangle, dec=float(row[3])*u.deg)
            cs = c.to_string("hmsdms")
            ra, dec = cs.split(' ')
            self.grid_data.SetCellValue(row_idx, 2, ra[:11])
            self.grid_data.SetCellValue(row_idx, 3, dec[:12])
            self.grid_data.SetCellValue(row_idx, 4, row[4])
            self.grid_data.SetCellValue(row_idx, 5, row[5])
            self.grid_data.SetCellValue(row_idx, 7, fmtflt(row[7]))
            self.grid_data.SetCellValue(row_idx, 8, fmtflt(row[8]))
            self.grid_data.SetCellValue(row_idx, 6, fmtflt(row[6], 4))
            self.grid_data.SetCellValue(row_idx, 9, fmtflt(row[9]))
            self.grid_data.SetCellValue(row_idx, 10, fmtflt(row[10]))
            self.grid_data.SetCellValue(row_idx, 11, row[11])
            self.grid_data.SetCellValue(row_idx, 12, row[12])
    
    def select_row(self, pos: int) -> None:
        self.grid_data.SelectRow(pos)
