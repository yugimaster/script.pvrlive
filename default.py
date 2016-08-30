# -*- coding: utf8 -*-

import os
import sys
import xbmc
import xbmcaddon


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_DATA_PATH = xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID).decode("utf-8")
sys.path.append(xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib')))
from WindowManager import wm


class Main:

    def __init__(self):
        xbmc.log("version %s started" % ADDON_VERSION)
        # xbmcgui.Window(10000).setProperty("Addon.IsLaunched", "True")
        # xbmcgui.Window(10000).setProperty("Addon.ChinaCinema", "on")
        wm.open_pvr_window()

if (__name__ == "__main__"):
    Main()
xbmc.log('finished')
