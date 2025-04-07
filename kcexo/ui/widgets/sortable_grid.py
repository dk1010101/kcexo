# -*- coding: UTF-8 -*-
import inspect
from typing import List, Any, Callable

import numpy as np

import astropy.units as u
from astropy.time import Time

import wx
import wx.grid

from .plot_cell_renderer import PlotCellRenderer


class GridData():
    """Wrapper around grid data"""
    def __init__(self,
                 data: List[List[Any]],
                 col_names: List[str],
                 col_widths: List[float]|None = None,
                 col_formatting: List[Callable]|None = None,
                 col_graph_prefix: str = "GRAPH_",
                 row_height: int|None = None) -> None:
        """Create a grid data bundle.

        Args:
            data (List[List[Any]]): Actual data - a list of rows of data.
            col_names (List[str]): List of column names.
            col_widths (List[float] | None, optional): List of column widths. Defaults to None meaning that they will be inferred.
            col_formatting (List[Callable] | None, optional): List of functions that will be used to render each column. Defaults to None meaning that they will be just pass-throughs.
            col_graph_prefix (str, optional): Prefix used to denote which cells should be rendered as graphs. Defaults to "GRAPH_".
            row_height (int | None, optional): Heigh of each row. Mainly useful when rendering plots. Defaults to None meaning that it will be inferred.
        """
        if len(data[0]) != len(col_names):
            raise ValueError("Number of columns in the data and the number of column names must match!")
        if col_widths and len(col_widths) != len(col_names):
            raise ValueError("Number of col widths (when provided) must be the same as the number of columns")
        if col_formatting and len(col_formatting) != len(col_names):
            raise ValueError("Number of col formatting functions (when provided) must be the same as the number of columns")
                
        self.data: List[List[Any]] = data
        self.col_names: List[str] = col_names
        self.col_widths: List[float]
        if col_widths:
            self.col_widths = col_widths
        else:
            self.col_widths = []
        self.col_formatting: List[Callable]
        if col_formatting:
            self.col_formatting = col_formatting
        else:
            self.col_formatting = [lambda x: x] * len(self.col_names)
        self.col_graph_prefix: str = col_graph_prefix
        self.plot_column_idx: list = []
        
        for idx, c in enumerate(self.col_names):
            if c.startswith(self.col_graph_prefix):
                self.plot_column_idx.append(idx)
        
        if not col_formatting and self.plot_column_idx:
            for i in self.plot_column_idx:
                self.col_formatting[i] = PlotCellRenderer
        
        self.row_height: int
        if row_height:
            self.row_height = row_height
        else:
            if self.plot_column_idx:
                self.row_height = 250  # default if we have a plot
            else:
                self.row_height = 25  # sensible default
                
    def __len__(self):
        """Length of this class is just the number of rows of data."""
        return len(self.data)
            

class SortableGrid(wx.grid.Grid):
    """Simple grid control that supports click-on-column-name for sorting and cells with images."""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.data: GridData = None
        self.columns = []
        self.plot_column_index = []
        self.current_sort_col = None
        self.sort_ascending = True
        self.plot_column_prefix = ""
        
        self.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        
        self.CreateGrid(1, 1)
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
        self.Bind(wx.EVT_SIZE, self.on_size)  # For initial drawing and resize
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_cell_changed) #redraw when cell value changes
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll) #handle scrolling
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_select) #redraw after selection change
    
    #########################
    # API

    def set_data(self, 
                 data: GridData|None) -> None:
        """Set the initial dataset, populate the grid and establish the bindings.

        Args:
            data (GridData): List of column-name to data mappings, one for each row.

        Raises:
            ValueError: If the plot prefix is not found in the list of columns.
        """
        self.data = data
        
        if not data or len(data)==0:
            self.columns = []
            self.plot_column_index = []
            self.ClearGrid()
            if self.GetNumberCols() > 0:
                self.DeleteCols(0, self.GetNumberCols())
            if self.GetNumberRows() > 0:
                self.DeleteRows(0, self.GetNumberRows())
            return
        else:
            self.columns = data.col_names

            self.ClearGrid()

            num_cols = self.GetNumberCols()
            num_rows = self.GetNumberRows()
            num_cols_new = len(self.columns)
            num_rows_new = len(self.data)

            if num_cols != num_cols_new or num_rows != num_rows_new:
                
                if num_cols > num_cols_new:
                    self.DeleteCols(0, num_cols - num_cols_new)
                elif num_cols < num_cols_new:
                    self.AppendCols(num_cols_new - num_cols)
                
                if num_rows > num_rows_new:
                    self.DeleteRows(0, num_rows - num_rows_new)
                elif num_rows < num_rows_new:
                    self.AppendRows(num_rows_new - num_rows)

            for row in range(self.GetNumberRows()):
                self.SetRowSize(row, self.data.row_height)
                
            for idx, w in enumerate(self.data.col_widths):
                self.SetColSize(idx, w)
                
            if not self.data.col_widths:
                for idx in self.plot_column_index:
                    self.SetColSize(idx, 300)

            self._populate_grid()

    def refresh_data(self, 
                     new_data: GridData, 
                     ) -> None:
        """Refreshes the grid with new data."""
        self.set_data(new_data)
        self._populate_grid()
            
    #########################
    # Helpers         

    def _populate_grid(self) -> None:
        """Populates grid with data, renders plots to images, sets renderer."""
        if len(self.data)==0:
            return

        for row_idx, row_data in enumerate(self.data.data):
            for col_idx, col_name in enumerate(self.columns):
                if row_idx == 0:
                    if col_name.startswith(self.plot_column_prefix):
                        name = col_name[len(self.plot_column_prefix):]
                    else:
                        name = col_name
                    self.SetColLabelValue(col_idx, name)
                
                fmt_fn = self.data.col_formatting[col_idx]
                if inspect.isclass(fmt_fn) and issubclass(fmt_fn, wx.grid.GridCellRenderer):
                    self.SetCellRenderer(row_idx, col_idx, fmt_fn(row_data[col_idx]))
                else:
                    self.SetCellValue(row_idx, col_idx, fmt_fn(row_data[col_idx]))

    def _sort_data(self, col_name: str) -> None:
        """Sorts the data (excluding the plot data) based on col_name."""
        col_idx = self.columns.index(col_name)
        if col_idx not in self.plot_column_index:
             self.data.data.sort(key=lambda item: item[col_idx], reverse=not self.sort_ascending)

    #########################
    # EVENTS
    
    def on_size(self, event):
        self.ForceRefresh()  # Force a redraw on resize
        event.Skip()

    def on_scroll(self, event):
        self.ForceRefresh() #force redraw on scroll
        event.Skip()

    def on_cell_changed(self, event):
        self.ForceRefresh()
        event.Skip()

    def on_range_select(self, event):
        if event.Selecting():
            self.ForceRefresh()
            event.Skip()

    def on_label_click(self, event):
        """Handles column label clicks for sorting."""
        col = event.GetCol()
        if col == -1 or col == self.plot_column_index:
            return

        if self.current_sort_col == col:
            self.sort_ascending = not self.sort_ascending
        else:
            self.current_sort_col = col
            self.sort_ascending = True

        self._sort_data(self.columns[col])
        self._populate_grid()  # Repopulate after sorting

        for i in range(len(self.columns)):  # pylint:disable=consider-using-enumerate
            if i == col:
                label = f"{self.columns[i]} ▲" if self.sort_ascending else f"{self.columns[i]} ▼"
                self.SetColLabelValue(i, label)
            elif i != self.plot_column_index:
                self.SetColLabelValue(i, self.columns[i])

def col_fmt_str(v: Any) -> str:
    """Convert anything in to a string."""
    return str(v)

def col_fmt_float(v: float|np.float32|np.float64|np.float16, 
                  precision: int=2) -> str:
    """Convert a float in to a string up to some precision (2dp being the default)."""
    if np.isnan(v):
        return "--"
    return f"{float(v):.{precision}f}"

def col_fmt_timeonly(v: Time) -> str:
    """Convert `Time` in to string keeping only the time part."""
    s = v.to_string()
    return s[11:19]

def col_fmt_length(v: u.Quantity['length'], 
                     target_unit: Any=u.mm) -> str:
    """Convert a length Quantity in to some other length (mm being the default) as a string."""
    return str(v.to(target_unit))

def col_fmt_length_as_f(v: u.Quantity['length'], 
                        target_unit: Any=u.mm) -> str:
    """Convert a length Quantity in to some other length (mm being the default) as a string."""
    return str(v.to(target_unit).value)

def col_fmt_quantity_as_f(v: u.Quantity) -> str:
    """Convert quantity to string via float"""
    return str(v.value)
