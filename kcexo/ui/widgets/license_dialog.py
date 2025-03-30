# -*- coding: UTF-8 -*-

import wx

class LicenseViewerDialog(wx.Dialog):
    def __init__(self, parent, title, text):
        super(LicenseViewerDialog, self).__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)
        self.text_ctrl.SetValue(text)

        close_button = wx.Button(self, label="Close")
        close_button.Bind(wx.EVT_BUTTON, self.OnClose)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(close_button, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetSize((600, 400))  # Set an initial size
        self.Layout()

    def OnClose(self, event):
        self.Destroy()