# -*- coding: UTF-8 -*-
# pylint:disable=invalid-name,missing-function-docstring


import wx


class ListCompleter(wx.TextCompleter):
    """Auto-complete for target text box to make life so much easier..."""
    def __init__(self, element_list: list):
        wx.TextCompleter.__init__(self)
        self.target_list = element_list
        self._iLastReturned = wx.NOT_FOUND
        self._sPrefix = ''

    def Start(self, prefix):
        """On first letter..."""
        self._sPrefix = prefix.lower()
        self._iLastReturned = wx.NOT_FOUND
        for item in self.target_list:
            if item.lower().startswith(self._sPrefix):
                return True
        # Nothing found
        return False

    def GetNext(self):
        """On subsequent letters..."""
        for i in range(self._iLastReturned+1, len(self.target_list)):
            if self.target_list[i].lower().startswith(self._sPrefix):
                self._iLastReturned = i
                return self.target_list[i]
        # No more corresponding item
        return ''