# sample_one.py

import wx
import wx.lib.mixins.inspection

# class MyFrame
# class MyApp

#---------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Widget Inspection Tool - WIT")

        #------------

        self.SetIcon(wx.Icon("icons/wxwin.ico"))

#---------------------------------------------------------------------------

class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):

        # Initialize the inspection tool.
        self.Init()

        #------------

        frame = MyFrame()
        frame.Show()
        self.SetTopWindow(frame)

        return True

#---------------------------------------------------------------------------

def main():
    app = MyApp(redirect=False)
    app.MainLoop()

#---------------------------------------------------------------------------

if __name__ == "__main__" :
    main()