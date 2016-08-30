# -*- coding: utf8 -*-

import xbmcgui
from Utils import *


class WindowXML(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self)
        self.window_type = "window"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.window_id)

    def set_container(self, container_id, items, focus=False):
        self.getControl(container_id).reset()
        self.getControl(container_id).addItems(create_listitems(items))
        if focus:
            self.setFocusId(container_id)


class DialogXML(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.window_type = "dialog"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.window_id)

    def set_container(self, container_id, items, focus=False, rePosition=True):
        listControl = self.getControl(container_id)
        selectedPosition = listControl.getSelectedPosition()
        listControl.reset()
        listControl.addItems(create_listitems(items))

        if rePosition is False:
            listControl.selectItem(selectedPosition)

        if focus:
            self.setFocusId(container_id)
