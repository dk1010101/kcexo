from contextlib import contextmanager
from pubsub import pub

import wx


@contextmanager
def prevent_tab_changes(msg: str = ""):
    """Make sure that tabs cannot be changed while whatever is happening is happening"""
    try:
        with wx.BusyCursor():
            if msg:
                pub.sendMessage("status.set", data=msg)
            pub.sendMessage("tabs.preventchange")
            yield
    finally:
        if msg:
            pub.sendMessage("status.clear")
        pub.sendMessage("tabs.allowchange")


@contextmanager
def update_status(msg: str):
    """Make sure that tabs cannot be changed while whatever is happening is happening"""
    try:
        with wx.BusyCursor():
            pub.sendMessage("status.set", data=msg)
            yield
    finally:
        pub.sendMessage("status.clear")