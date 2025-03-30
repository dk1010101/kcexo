# -*- coding: UTF-8 -*-
import wx


def new_command_event():
    """Generates a new `(command_event, binder)` tuple."""

    evttype = wx.NewEventType()

    class _Event(wx.PyCommandEvent):
        def __init__(self, wid, **kw):
            wx.PyCommandEvent.__init__(self, evttype, wid)
            self._getAttrDict().update(kw)

    return _Event, wx.PyEventBinder(evttype, 1)
