#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# cSpell:ignore kcexo

import importlib.resources as res

import wx
from kcexo.ui.planner.main_frame import MainFrame


def main():
    app = App(0)
    app.MainLoop()

class App(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        _icon = wx.NullIcon
        with res.path("kcexo.assets.planner", "icon.png") as path:
            _icon.CopyFromBitmap(wx.Bitmap(path.as_posix(), wx.BITMAP_TYPE_ANY))
        self.frame.SetIcon(_icon)
        return True

if __name__ == "__main__":
    main()
