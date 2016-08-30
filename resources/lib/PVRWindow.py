# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
from BaseClasses import *
from dialogs.DialogBaseInfo import DialogBaseInfo
from OnClickHandler import OnClickHandler
from WindowManager import wm
from pvr import EPGAPI
from library import LibraryFunctions
from Utils import *
from Utils import stop_play

ch = OnClickHandler()
LIBRARY = LibraryFunctions()
C_LIST_CHANNEL = 11


class PVR(WindowXML, DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(PVR, self).__init__(*args, **kwargs)
        self.MODE = ""
        self.DATA = self.get_channel_data()
        self.last_cha_position = 0

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.window_id)
        xbmcgui.Window(10000).setProperty("pvrwindowId", str(self.window_id))
        self.set_channel_list()

    def onAction(self, action):
        ch.serve_action(action, self.getFocusId(), self)

    def onClick(self, control_id):
        super(PVR, self).onClick(control_id)
        ch.serve(control_id, self)

    def set_channel_list(self):
        if not self.DATA:
            okDialog("获取直播数据失败")
            self.doClose()
            return
        else:
            channel_cid = LIBRARY._get_data("chinacinema_pvr_channel", "last", 0)
            self.getControl(C_LIST_CHANNEL).setVisible(False)
            self.window.setProperty("hide", "True")
            channel_list = self.init_channel_list(self.DATA)
            self.set_container(C_LIST_CHANNEL, channel_list)
            self.play_livestream(channel_cid)

    def play_livestream(self, channel_cid):
        if xbmc.Player().isPlayingVideo():
            if xbmc.getInfoLabel('VideoPlayer.Originaltitle') == "livetv":
                self.last_cha_position = int(xbmc.getInfoLabel('VideoPlayer.Studio'))
                self.switch_mode("play")
                return
            else:
                stop_play()
        if channel_cid is not None:
            channel_index = 0
            for item in self.DATA:
                if item['id'] == channel_cid:
                    url = item['urls'][0]['url']
                    title = item['title']
                    break
                channel_index += 1
            if channel_index < len(self.DATA):
                self.last_cha_position = channel_index
                self.getControl(C_LIST_CHANNEL).selectItem(self.last_cha_position)
                self.play_channel(channel_cid, url, title)
            else:
                urls = self.DATA[0]['urls']
                self.play_channel(self.DATA[0]['id'], urls[0]['url'], self.DATA[0]['title'])
        else:
            urls = self.DATA[0]['urls']
            self.play_channel(self.DATA[0]['id'], urls[0]['url'], self.DATA[0]['title'])

    def get_channel_data(self):
        listitems = []
        while (not xbmc.abortRequested):
            data = LIBRARY.fetch_pvr_channel_list()
            if data is None:
                return listitems
            else:
                listitems = data.get("list", [])
                break
        return listitems

    def init_channel_list(self, listitem):
        if not listitem:
            return listitem
        lists = listitem
        for (count, item) in enumerate(lists):
            lists[count]['title'] = item['title']
            lists[count]['id'] = item['id']
            lists[count]['url'] = item['urls'][0]['url']
            lists[count]['columnId'] = item['columnId']
        return lists

    @busy_dialog
    def play_channel(self, channel_cid, mop_url, title):
        self.switch_mode("play")
        if not mop_url:
            return
        url = EPGAPI.get_live_play(channel_cid, mop_url)
        stop_play()
        listitem = xbmcgui.ListItem("livetv")
        listitem.setInfo("video", {"Title": "直播 {name}".format(name=title.encode('utf8'))})
        listitem.setInfo("video", {"Originaltitle": "livetv"})
        listitem.setInfo("video", {"Studio": str(self.last_cha_position)})
        xbmc.Player().play(url, listitem=listitem, windowed=True)
        LIBRARY._set_data("chinacinema_pvr_channel", channel_cid, "last", 0)

    def change_channel(self):
        control = self.getControl(C_LIST_CHANNEL)
        item = control.getSelectedItem()
        self.last_cha_position = control.getSelectedPosition()
        sid = item.getProperty("id")
        url = item.getProperty("url")
        title = item.getProperty("title")
        self.play_channel(sid, url, title.decode('utf8'))
        xbmc.sleep(1000)

    def switch_mode(self, mode):
        if mode == "play":
            if mode != self.MODE:
                self.window.setProperty("hide", "True")
            self.getControl(C_LIST_CHANNEL).setVisible(True)
            self.setFocusId(C_LIST_CHANNEL)
            self.getControl(C_LIST_CHANNEL).selectItem(self.last_cha_position)
        elif mode == "channels":
            self.getControl(C_LIST_CHANNEL).setVisible(True)
            self.window.setFocusId(C_LIST_CHANNEL)
        self.MODE = mode
        self.window.setProperty("mode", mode)

    @run_async
    def hide_menu_async(self):
        while True:
            xbmc.sleep(100)
            if xbmc.getCondVisibility("System.IdleTime(5)"):
                self.switch_mode("play")
                break

    def start_osd(self, startSeek):
        if not xbmc.Player().isPlayingVideo():
            return
        seekPos = 100
        dialog = wm.show_pvr_osd(seekPos, startSeek, True)
        if dialog.isQuit:
            self.doClose()
        elif dialog.isSeek and seekPos != dialog.PROGRESS_STATUS:
            pass
        del dialog

    def doClose(self):
        xbmcgui.Window(10000).clearProperty("pvrwindowId")
        self.close()

    @ch.click(C_LIST_CHANNEL)
    def click_channel_item(self):
        if self.MODE == "play":
            self.start_osd(False)
        else:
            control = self.getControl(C_LIST_CHANNEL)
            pos = control.getSelectedPosition()
            if pos != self.last_cha_position:
                item = control.getSelectedItem()
                sid = item.getProperty("id")
                url = item.getProperty("url")
                title = item.getProperty("title")
                self.last_cha_position = pos
                self.play_channel(sid, url, title.decode('utf8'))
            xbmc.sleep(1000)

    @ch.action("up", "*")
    def action_up(self):
        if self.MODE == "play" and (xbmc.getInfoLabel('VideoPlayer.Originaltitle') == "livetv" or not xbmc.Player().isPlayingVideo()):
            self.change_channel()

    @ch.action("down", "*")
    def action_down(self):
        if self.MODE == "play" and (xbmc.getInfoLabel('VideoPlayer.Originaltitle') == "livetv" or not xbmc.Player().isPlayingVideo()):
            self.change_channel()

    @ch.action("back", "*")
    @ch.action("previousmenu", "*")
    def exit_script(self):
        if self.MODE == "channels":
            self.doClose()
        elif self.MODE == "play":
            self.window.clearProperty("hide")
            if xbmc.getInfoLabel("VideoPlayer.Originaltitle") == "livetv" or not xbmc.Player().isPlayingVideo():
                self.switch_mode("channels")
            self.hide_menu_async()
