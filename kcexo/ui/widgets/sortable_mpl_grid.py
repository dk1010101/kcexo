from typing import List, Dict, Any, Callable

import wx
import wx.grid

from .plot_cell_renderer import PlotCellRenderer

class GridData():
    col_names: List[str]
    col_widths: List[float]
    col_formating: List[Callable|None]
    data: List[List[Any]]


class SortableMatplotlibCellGrid(wx.grid.Grid):
    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.data: List[Dict[str, Any]] = []
        self.columns = []
        self.plot_column_index = []
        self.current_sort_col = None
        self.sort_ascending = True
        self.plot_column_prefix = ""
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
        self.Bind(wx.EVT_SIZE, self.on_size)  # For initial drawing and resize
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_cell_changed) #redraw when cell value changes
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll) #handle scrolling
    
    #########################
    # API

    def set_data(self, 
                 data: List[Dict[str, Any]], 
                 plot_column_prefix: str="GRAPH_") -> None:
        """Set the initial dataset, populate the grid and establish the bindings.

        Args:
            data (List[Dict[str, Any]]): List of column-name to data mappings, one for each row.
            plot_column_prefix (str, optional): Name of the column prefix that needs to be rendered as a graph. 
                The prefix will be dropped from the column name. Defaults to "GRAPH_".

        Raises:
            ValueError: If the plot prefix is not found in the list of columns.
        """
        self.data = data
        self.plot_column_prefix = plot_column_prefix
        
        if not data:
            self.columns = []
            self.plot_column_index = []
            self.ClearGrid()
            if self.GetNumberCols() > 0:
                self.DeleteCols(0, self.GetNumberCols())
            if self.GetNumberRows() > 0:
                self.DeleteRows(0, self.GetNumberRows())
            return
        else:
            self.columns = list(data[0].keys())
            c: str
            for idx, c in enumerate(self.columns):
                if c.startswith(plot_column_prefix):
                    self.plot_column_index.append(idx)
            if not self.plot_column_index:
                raise ValueError(f"Plot column '{plot_column_prefix}' not found in data.")

        if self.GetNumberCols() != len(self.columns) or (self.data and self.GetNumberRows() != len(self.data)):
            self.ClearGrid()
            if self.GetNumberCols() > 0:
                self.DeleteCols(0, self.GetNumberCols())
            if self.GetNumberRows() > 0:
                self.DeleteRows(0, self.GetNumberRows())
            self.CreateGrid(len(self.data), len(self.columns))

        for row in range(self.GetNumberRows()):
            self.SetRowSize(row, 150)
        self.SetColSize(self.plot_column_index, 250)

        self._populate_grid()
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_select) #redraw after selection change

    def refresh_data(self, 
                     new_data: List[Dict[str, Any]], 
                     plot_column_prefix: str="GRAPH_") -> None:
        """Refreshes the grid with new data."""
        new_columns = list(new_data[0].keys()) if new_data else []
        if new_columns != self.columns:
            self.set_data(new_data, plot_column_prefix) #recreate if columns changed.
        else:
            self.data = new_data
            self._populate_grid()
            
    #########################
    # Helpers         

    def _populate_grid(self) -> None:
        """Populates grid with data, renders plots to images, sets renderer."""
        if len(self.data)==0:
            return

        for row_idx, row_data in enumerate(self.data):
            for col_idx, col_name in enumerate(self.columns):
                if row_idx == 0:
                    if col_name.starts_with(self.plot_column_prefix):
                        name = col_name[len(self.plot_column_prefix):]
                    else:
                        name = col_name
                    self.SetColLabelValue(col_idx, name)
                if col_idx in self.plot_column_index:
                  # Set the custom cell renderer for the plot column
                  self.SetCellRenderer(row_idx, col_idx, PlotCellRenderer(row_data[col_name]))
                else:
                    self.SetCellValue(row_idx, col_idx, str(row_data[col_name]))

    def _sort_data(self, col_name: str) -> None:
        """Sorts the data (excluding the plot data) based on col_name."""
        col_idx = self.columns.index(col_name)
        if col_idx not in self.plot_column_index:
             self.data.sort(key=lambda item: item[col_name], reverse=not self.sort_ascending)

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

    