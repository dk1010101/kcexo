# -*- coding: UTF-8 -*-
import wx
import io


class PlotCellRenderer(wx.grid.GridCellRenderer):
    """Render an image as a cell in a grid"""
    def __init__(self, plot_image_data):
        wx.grid.GridCellRenderer.__init__(self)
        self.plot_image_data = plot_image_data  # This is now image data (bytes)
        self.bitmap = None  # Store the wx.Bitmap

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """_summary_

        Args:
            grid (_type_): unused
            attr (_type_): cell attributes
            dc (_type_): _description_
            rect (_type_): Size of the cell in pixels
            row (_type_): unused
            col (_type_): unused
            isSelected (bool): Is the cell selected?
        """
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