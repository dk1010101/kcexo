# -*- coding: UTF-8 -*-
import importlib.resources as res
import wx.adv
from wx.lib.wordwrap import wordwrap

def show_about_box(parent):
    info = wx.adv.AboutDialogInfo()
    _icon = wx.NullIcon
    with res.path("kcexo.assets.planner", "icon.png") as path:
        _icon.CopyFromBitmap(wx.Bitmap(path.as_posix(), wx.BITMAP_TYPE_ANY))    
    info.Icon = _icon
    info.Name = "Exoplanet Planner"
    info.Version = "0.0.1"
    info.Copyright = "(c) 2025 Daniel Kustrin"
    s = """
A tool to help you plan your observations.
"""
    info.Description = wordwrap(s, 500, wx.ClientDC(parent), margin=5)
    # Then we call wx.AboutBox giving it that info object
    wx.adv.AboutBox(info)
