import re
import string
import wx


class UTCOffsetValidator(wx.Validator):
    """WX validator for numeric UTC offsets"""    
    pattern = re.compile("^[+-]?[0-9]+(.[0-9]*)?$")
        
    def __init__(self):
        wx.Validator.__init__(self)
        # self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return UTCOffsetValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        ok = self.pattern.match(val) is not None
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
        
        ck = chr(key)
        if ck in string.digits or ck in ['-', '.', '+']:
            event.Skip()
            return

        if not wx.Validator.IsSilent():
            wx.Bell()

        return
