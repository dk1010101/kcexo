# -*- coding: UTF-8 -*-
# pylint:disable=invalid-name,missing-function-docstring,unused-argument
import io

import wx


class PlotCellRenderer(wx.grid.GridCellRenderer):
    """Render an image as a cell in a grid"""
    def __init__(self, plot_image_data):
        wx.grid.GridCellRenderer.__init__(self)
        self.plot_image_data, self.best_size = plot_image_data  # This is now image data (bytes)
        self.bitmap = None  # Store the wx.Bitmap

    def Clone(self):
        return PlotCellRenderer((self.plot_image_data, self.best_size))

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        if self.bitmap is None and self.plot_image_data:
            # Convert image data to wx.Bitmap
            stream = io.BytesIO(self.plot_image_data)
            image = wx.Image(stream, wx.BITMAP_TYPE_ANY) #detect image type automatically
            # Scale the image to fit the cell
            scaled_image = image.Scale(rect.width, rect.height, wx.IMAGE_QUALITY_HIGH)
            self.bitmap = scaled_image.ConvertToBitmap()

        dc.SetBackgroundMode(wx.SOLID)
        if isSelected:
            dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)))
        else:
            dc.SetBrush(wx.Brush(attr.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)

        if self.bitmap:
            dc.DrawBitmap(self.bitmap, rect.x, rect.y, True)
    
    def GetMaxBestSize(self, grid, attr, dc):
        return wx.Size(width=self.best_size[0], height=self.best_size[1])
    
    def GetBestSize(self, grid, attr, dc, row, col):
        return wx.Size(width=self.best_size[0], height=self.best_size[1])
    
    def GetBestWidth(self, grid, attr, dc, row, col, height):
        return self.best_size[0]
     
    def GetBestHeight(self, grid, attr, dc, row, col, height):
        return self.best_size[1]
