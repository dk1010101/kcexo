# -*- coding: UTF-8 -*-
# cSpell:ignore hmsdms otypes
from typing import Any

import wx

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table


class GridPanel(wx.Panel):
    """Bottom pane panel for the data grid"""
    
    grid_col_tooltops = [
        "SIMBAD Star Name",
        "SIMBAD ID",
        "Right Ascension",
        "Declination",
        """
SIMBAD star type

There are many star types including:
  Ma* - massive stars (bC*, sg*, s*r, s*y, s*b, WR*, N*, Psr ...)
  Y*  - young stars (Or*, TT*, Ae*, HH ...)
  MS* - main seq stars (Be*, BS*, SX, gD*, dS* ...)
  Ev* - evolved stars (RG*, HS*, HB*, RR*, WV*, Ce*, cC*
             C*, S*, LP*, AB*, Mi*, OH*, pA*, RV*, PN, WD...)
  Pe* - Chemically peculiar stars (a2*, RC* ...)
  ** - multiple stars (EB*, El*, SB*, RS*, BY*, Sy*, XB*, CV*, No* ...)
  EM* - emission line stars
  SN* - supernovae
  LM* - low mass stars inc brown dwarfs (BD*)
  Pl  - planets
  V*  - variable stars (Ir*,  Er*, Ro*, Pu* ...)
  PM* - high proper motion stars
  HV* - high velocity stars

etc. Generally speaking they are all variable to some extent so
just stick to * for comparators although PM* and HV* may not be
variable (but they could be...).

Google 'SIMBAD otypes' and enjoy!

""",
        """
Variability Type

Sometimes this may suggest variability when the star is
not marked as variable. In these cases exercise caution
as some variability may be present.
""",
        "Spherical Distance (degrees)",
        """
Gaia Colour Index

This is a difference between Gaia Blue and Gaia Red and it shows
how Blue or Red a star is. Since Gaia filter bands are a lot wider
than Johnson-Cousins UBVRI ones. Gaia Blue (Gbp) covers a range
from mid-U through all of V and to mid-R while Gaia Red (Gbr) covers
a range from mid-R to I and beyond. THese differences indicate that 
Gaia colour will not be (linearly) correlated with the B-V colour. 

""",
        """
Johnson-Cousins Colour Index

Colour of the comparator stars has a big influence on the quality of
photometry as, generally speaking, similarly coloured stars will behave
more similarly when images then stars of other colours. B-V is the 
traditional measurement of the star colour and thus temperature.
Generally speaking, the bigger the number the redder the star.

Common B-V classifications are:

B-V >= 1.4

Red coloured, M class when on main branch, K4-M9 as a giant of K3-M0 as supergiant stars. 
Examples would be Antares and Betelgeuse.

B-V between 0.8 and 1.4

Orange K class stars on main branch. As giants they would be G4-K3 and as supergiants G1-K2.
Examples would be Arcturus and Pollux.

B-V between 0.6 and 0.8

Yellow stars in G class. G0-G3 as giants and F8-G0 as supergiants. Our Sun is a good example.

B-V between 0.3 and 0.6

Green F class stars. Supergiants would be F4-F7. Procyon is an examplar.

B-V between 0.0 and 0.3

White A class stars with supergiants in A0-F3. Sirius and Vega are prototypical and Vega us
often used as the fixed point from which other stars are measured.

B-V < 0.0

Blue stars in the OB class. Spica and Rigel are good examples.

""",
    "Gaia G magnitude",
    "Johnson B magnitude\n\nNote - we don't filter on B since B is not really used in exoplanet imaging.",
    "Johnson V magnitude",
    "Johnson R magnitude",
    "Gaia ID",
    "TESS Input Catalogue ID"
    ]
    
    
    def __init__(self, parent, wid=wx.ID_ANY, 
                 background_colour: wx.Colour=wx.WHITE, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 name='topPanel'):
        super().__init__(parent=parent, id=wid, pos=pos, size=size, name=name)
        self.prev_rowcol = [None, None]
        self.data: Table
        
        self.controls_collection = []
        self.background_colour = background_colour

        self.grid_data = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_data.CreateGrid(20, 15)
        self.grid_data.SetColLabelValue(0, "Name")
        self.grid_data.SetColLabelValue(1, "oid")
        self.grid_data.SetColLabelValue(2, "RA")
        self.grid_data.SetColLabelValue(3, "DEC")
        self.grid_data.SetColLabelValue(4, "Type")
        self.grid_data.SetColLabelValue(5, "Var Type")
        self.grid_data.SetColLabelValue(6, "Distance")
        self.grid_data.SetColLabelValue(7, "Gbp-Grp")
        self.grid_data.SetColLabelValue(8, "B-V")
        self.grid_data.SetColLabelValue(9, "G")
        self.grid_data.SetColLabelValue(10, "B")
        self.grid_data.SetColLabelValue(11, "V")
        self.grid_data.SetColLabelValue(12, "R")
        self.grid_data.SetColLabelValue(13, "Gaia ID")
        self.grid_data.SetColLabelValue(14, "TIC")
        
        self.grid_data.SetColSize(0, 23*5)   # Name
        self.grid_data.SetColSize(1, 11*5)   # oid
        self.grid_data.SetColSize(2, 17*5)   # RA
        self.grid_data.SetColSize(3, 18*5)   # DEC
        self.grid_data.SetColSize(4, 8*5)    # Type
        self.grid_data.SetColSize(5, 11*5)   # Var Type
        self.grid_data.SetColSize(6, 11*5)   # Distance
        self.grid_data.SetColSize(7, 11*5)   # Gbp-Grp
        self.grid_data.SetColSize(8, 9*5)    # B-V
        self.grid_data.SetColSize(9, 9*5)    # G
        self.grid_data.SetColSize(10, 9*5)   # B
        self.grid_data.SetColSize(11, 9*5)   # V
        self.grid_data.SetColSize(12, 9*5)   # R
        self.grid_data.SetColSize(13, 34*5)  # Gaia ID
        self.grid_data.SetColSize(14, 20*5)  # TIC
        
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
        self.grid_data.GetGridColLabelWindow().Bind(wx.EVT_MOTION, self.on_grid_motion)
    
    def resize_grid(self) -> None:
        """Resize the grid to match the data that we have."""
        current, new = (self.grid_data.GetNumberRows(), len(self.data))
        if new < current:
            self.grid_data.DeleteRows(0, current-new, True)
        if new > current:
            self.grid_data.AppendRows(new-current)
    
    def update_grid(self, new_data: Table) -> None:
        """Update the grid with the new data."""
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

            self.grid_data.SetCellValue(row_idx, 0, row[0])  # Name
            self.grid_data.SetCellValue(row_idx, 1, str(row[1]))  # oid
            c = SkyCoord(ra=float(row[2])*u.deg, dec=float(row[3])*u.deg)
            cs = c.to_string("hmsdms")
            ra, dec = cs.split(' ')
            self.grid_data.SetCellValue(row_idx, 2, ra[:11])            # RA
            self.grid_data.SetCellValue(row_idx, 3, dec[:12])           # DEC
            self.grid_data.SetCellValue(row_idx, 4, row[4])             # Type
            self.grid_data.SetCellValue(row_idx, 5, row[5])             # Var Type
            self.grid_data.SetCellValue(row_idx, 6, fmtflt(row[6], 4))  # Distance
            self.grid_data.SetCellValue(row_idx, 7, fmtflt(row[13]))    # Gbp-GRp
            self.grid_data.SetCellValue(row_idx, 8, fmtflt(row[7]))     # B-V
            self.grid_data.SetCellValue(row_idx, 9, fmtflt(row[14]))    # G
            self.grid_data.SetCellValue(row_idx, 10, fmtflt(row[8]))    # B
            self.grid_data.SetCellValue(row_idx, 11, fmtflt(row[9]))    # V
            self.grid_data.SetCellValue(row_idx, 12, fmtflt(row[10]))   # R
            self.grid_data.SetCellValue(row_idx, 13, str(row[11]))      # Gaia ID
            self.grid_data.SetCellValue(row_idx, 14, row[12])           # TIC
            
    
    def select_row(self, pos: int) -> None:
        """Select a row based on position."""
        self.grid_data.SelectRow(pos)
    
    def on_grid_motion(self, evt):
        """Show tooltips"""
        # evt.GetRow() and evt.GetCol() would be nice to have here,
        # but as this is a mouse event, not a grid event, they are not
        # available and we need to compute them by hand.
        x, y = self.grid_data.CalcUnscrolledPosition(evt.GetPosition())
        row = self.grid_data.YToRow(y)
        col = self.grid_data.XToCol(x)

        if (row,col) != self.prev_rowcol and row >= 0 and col >= 0:
            self.prev_rowcol[:] = [row,col]
            hinttext = self.grid_tooltip_get(row, col)
            if hinttext is None:
                hinttext = ''
            self.grid_data.GetGridColLabelWindow().SetToolTip(hinttext)
        evt.Skip()
    
    def grid_tooltip_get(self, row, col) -> str:
        """Show tooltips"""
        return self.grid_col_tooltops[col]
