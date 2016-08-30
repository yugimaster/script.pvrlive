# -*- coding: utf8 -*-

from Utils import *
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
PVR_XML = "script-PVR.xml"
PVROSD_XML = "script-PVROSD.xml"


class WindowManager(object):

    def __init__(self):
        self.window_stack = []

    def add_to_stack(self, window):
        """
        add window / dialog to global window stack
        """
        self.window_stack.append(window)

    def pop_stack(self):
        """
        get newest item from global window stack
        """
        if self.window_stack:
            dialog = self.window_stack.pop()
            xbmc.sleep(300)
            dialog.doModal()

    def show_pvr_osd(self, pos, startSeek, showSeekTime, prev_window=None):
        """
        open pvr osd dialog, deal with window stack
        """
        from dialogs.DialogPVROSD import PVROSD
        dialog = PVROSD(PVROSD_XML, ADDON_PATH, pos=pos, startSeek=startSeek, showSeekTime=showSeekTime)
        self.open_dialog(dialog, prev_window)
        return dialog

    def open_pvr_window(self, prev_window=None):
        """
        open pvr window, deal with window stack
        """
        import PVRWindow
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        dialog = PVRWindow.PVR(PVR_XML, ADDON_PATH)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_dialog(self, dialog, prev_window):
        if dialog:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()
            self.pop_stack()
        else:
            notify(LANG(32143))

wm = WindowManager()
