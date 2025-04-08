#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# cSpell:ignore kcexo
import logging
import importlib.resources as res

import wx
import wx.lib.mixins.inspection

from kcexo.ui.planner.main_frame import MainFrame


def setup_logger():
    logger_formatter = logging.Formatter("%(name)s\t%(levelname)s\t%(message)s")
    logger_stream_handler = logging.StreamHandler()
    logger_stream_handler.setLevel(logging.DEBUG)
    logger_stream_handler.setFormatter(logger_formatter)
    logger_file_handler = logging.FileHandler("./kcexo.log", mode = "w")
    logger_file_handler.setLevel(logging.DEBUG)
    logger_file_handler.setFormatter(logger_formatter)
    logger = logging.getLogger("KCEXO")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logger_stream_handler)
    logger.addHandler(logger_file_handler)
    logger.info("Logger configured.")
    return logger


def main():
    app = App(0)
    app.MainLoop()


class App(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()
        
        self.frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        _icon = wx.NullIcon
        with res.path("kcexo.assets.planner", "icon.png") as path:
            _icon.CopyFromBitmap(wx.Bitmap(path.as_posix(), wx.BITMAP_TYPE_ANY))
        self.frame.SetIcon(_icon)
        return True

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = setup_logger()
    log.critical("CRITICAL")
    log.error("ERROR")
    log.exception("EXCEPTION")
    log.info("I Starting application")
    log.debug("D Starting application")
    
    main()
