from typing import List, Any, Callable

import wx
import wx.grid

from .plot_cell_renderer import PlotCellRenderer


class GridData():
    """Wrapper around grid data"""
    def __init__(self,
                 data: List[List[Any]],
                 col_names: List[str],
                 col_widths: List[float]|None = None,
                 col_formating: List[Callable]|None = None,
                 col_graph_prefix: str = "GRAPH_",
                 row_height: int|None = None) -> None:
        """Create a grid data bundle.

        Args:
            data (List[List[Any]]): Actual data - a list of rows of data.
            col_names (List[str]): List of column names.
            col_widths (List[float] | None, optional): List of column widths. Defaults to None meaning that they will be inferred.
            col_formating (List[Callable] | None, optional): List of functions that will be used to render each column. Defaults to None meaning that they will be just pass-throughs.
            col_graph_prefix (str, optional): Prefix used to denote which cells should be rendered as graphs. Defaults to "GRAPH_".
            row_height (int | None, optional): Heigh of each row. Mainly useful when rendering plots. Defaults to None meaning that it will be inferred.
        """
        if len(data[0]) != len(col_names):
            raise ValueError("Number of columns in the data and the number of column names must match!")
        if col_widths and len(col_widths) != len(col_names):
            raise ValueError("Number of col widths (when provided) much be the same as the number of columns")
        if col_formating and len(col_formating) != len(col_names):
            raise ValueError("Number of col formatting functions (when provided) much be the same as the number of columns")
        
        self.data: List[List[Any]] = data
        self.col_names: List[str] = col_names
        self.col_widths: List[float]
        if col_widths:
            self.col_widths = col_widths
        else:
            self.col_widths = []
        self.col_formating: List[Callable]
        if col_formating:
            self.col_formating = col_formating
        else:
            self.col_formating = [lambda x: x] * len(self.col_names)
        self.col_graph_prefix: str = col_graph_prefix
        self.plot_column_idx: list = []
        
        for idx, c in enumerate(self.col_names):
            if c.startswith(self.col_graph_prefix):
                self.plot_column_idx.append(idx)
        
        if not col_formating and self.plot_column_idx:
            for i in self.plot_column_idx:
                self.col_formating[i] = PlotCellRenderer
        
        self.row_height: int
        if row_height:
            self.row_height = row_height
        else:
            if self.plot_column_idx:
                self.row_height = 150  # default if we have a plot
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
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
        self.Bind(wx.EVT_SIZE, self.on_size)  # For initial drawing and resize
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_cell_changed) #redraw when cell value changes
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll) #handle scrolling
    
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

        if self.GetNumberCols() != len(self.columns) or (self.data and self.GetNumberRows() != len(self.data)):
            self.ClearGrid()
            if self.GetNumberCols() > 0:
                self.DeleteCols(0, self.GetNumberCols())
            if self.GetNumberRows() > 0:
                self.DeleteRows(0, self.GetNumberRows())
            self.CreateGrid(len(self.data), len(self.columns))

        for row in range(self.GetNumberRows()):
            self.SetRowSize(row, 150)
            
        for idx, w in enumerate(self.data.col_widths):
            self.SetColSize(idx, w)

        self._populate_grid()
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_select) #redraw after selection change

    def refresh_data(self, 
                     new_data: GridData, 
                     ) -> None:
        """Refreshes the grid with new data."""
        if new_data.col_names != self.columns:
            self.set_data(new_data)
        else:
            self.data = new_data
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
                    if col_name.starts_with(self.plot_column_prefix):
                        name = col_name[len(self.plot_column_prefix):]
                    else:
                        name = col_name
                    self.SetColLabelValue(col_idx, name)
                self.SetCellValue(row_idx, col_idx, self.data.col_formating[col_idx](row_data[col_idx]))

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

    