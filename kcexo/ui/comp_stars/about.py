# -*- coding: UTF-8 -*-
import importlib.resources as res
import wx.adv
from wx.lib.wordwrap import wordwrap

def show_about_box(parent):
    info = wx.adv.AboutDialogInfo()
    _icon = wx.NullIcon
    with res.path("kcexo.assets.comp_stars", "splash_44.png") as path:
        _icon.CopyFromBitmap(wx.Bitmap(path.as_posix(), wx.BITMAP_TYPE_ANY))    
    info.Icon = _icon
    info.Name = "Comparator Star Finder"
    info.Version = "0.0.1"
    info.Copyright = "(c) 2025 Daniel Kustrin"
    s = """
A simple tool that loads reduced FITS images and uses the metadata in the image to find the filed of view and all the stars in that field that could be used as comparators. It also returns known variable stars and highlights them in yellow so that they can be easily avoided.

Along with the stars in the field, the tool also shows colour and various magnitudes as well as the distance from the "main object" which is determined from the "OBJECT" FITS attribute. If this attribute is missing, the tool won't work. The name of the object is also assumed to be "canonical" (ie known to SIMBAD) and if the name cannot be found then FITS attributes OBJCTRA and OBJCTDEC will be used to get the main target coordinates. Again, if these are missing - you are on your own.

Once you load the image and have all the potential comparator/check stars highlighted, have a look at the colour (B-V) of the target (first row in the table) along with the magnitudes. You will want to find stars that are:

- non-variable (ie not highlighted in yellow)
- close
- have similar colour so they will have the B-V value that is similar to the target
- have similar magnitude
- are not saturated so be careful of stars that are brighter than the target

You will probably also find that the magnitude you are interested in, say, R is missing. This is where colour comes in.

If the image is not very visible you can use the stretching functions but be aware that stretching is a tricky process. You can also use your mouse to click-move the image and the mouse roller to zoom in and out. Clicking on a star will highlight it in the grid. You can also export the filtered grid to CSV if you really need to.

Be aware that, unfortunately, often there aren't any decent comparator stars and this is where your judgement comes in. Good luck!
"""
    info.Description = wordwrap(s, 500, wx.ClientDC(parent), margin=5)
    # Then we call wx.AboutBox giving it that info object
    wx.adv.AboutBox(info)
