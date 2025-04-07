# -*- coding: UTF-8 -*-
# pylint:disable=invalid-name,missing-function-docstring

import re
import string
import wx


class NumberValidator(wx.Validator):
    """Validate input for integers only"""
    
    pattern = re.compile("^[0-9]+$")
    minus_pattern = re.compile("^[-]?[0-9]+$")
    
    def __init__(self, allow_negative: bool=False):
        wx.Validator.__init__(self)
        self.allow_negative = allow_negative
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumberValidator(allow_negative=self.allow_negative)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        if self.allow_negative:
            p = self.minus_pattern
        else:
            p = self.pattern
        
        ok = p(val)
        if not ok:
            tc.SetBackgroundColour("pink")
            tc.SetFocus()
            tc.Refresh()
            return False
        else:
            tc.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            tc.Refresh()
            return True

    def OnChar(self, event):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key == wx.WXK_BACK or key > 255:
            event.Skip()
            return

        if chr(key) in string.digits or (self.allow_negative and chr(key) == '-'):
            event.Skip()
            return

        if not wx.Validator.IsSilent():
            wx.Bell()
        return