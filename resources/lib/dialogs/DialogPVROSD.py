# -*- coding: utf8 -*-

from Utils import *
from DialogBaseInfo import DialogBaseInfo
from OnClickHandler import OnClickHandler
from BaseClasses import DialogXML
from traceback import print_exc

ch = OnClickHandler()
C_BUTTON_STOP = 10
C_BUTTON_PLAY = 11
C_PROGRESS_NORMAL = 1400
C_PROGRESS_SPECIAL = 1500
C_SEEK_SLIDER = 1600
C_LABEL_TIME = 1700


class PVROSD(DialogXML, DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(PVROSD, self).__init__(*args, **kwargs)
        self.PROGRESS_STATUS = kwargs['pos']
        self.STARTSEEK = kwargs['startSeek']
        self.showSeekTime = kwargs['showSeekTime']
        self.isClose = False
        self.isQuit = False
        self.seek_point = -1
        self.isSeek = False

    def onInit(self):
        super(PVROSD, self).onInit()
        self.window_id = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.window_id)
        self.autoClose()
        self.set_process_status(self.PROGRESS_STATUS)
        self.getControl(C_LABEL_TIME).setLabel()
        if self.startSeek:
            self.setFocusId(C_SEEK_SLIDER)

    def onAction(self, action):
        ch.serve_action(action, self.getFocusId(), self)

    def onClick(self, control_id):
        super(PVROSD, self).onClick(control_id)
        ch.serve(control_id, self)

    @run_async
    def autoClose(self):
        while True:
            xbmc.sleep(100)
            if xbmc.getCondVisibility("System.IdleTime(3)") or self.isClose:
                self.close()
            elif xbmc.getCondVisibility("System.IdleTime(1)") and self.isSeek:
                self.close()
                break

    def set_process_status(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        self.PROGRESS_STATUS = percent
        if self.getFocusId() == C_SEEK_SLIDER:
            self.getControl(C_PROGRESS_NORMAL).setPercent(percent)
        else:
            self.getControl(C_PROGRESS_SPECIAL).setPercent(percent)
        if self.showSeekTime:
            self.getControl(C_LABEL_TIME).setLabel("-" + format)

    def format_time(self, time):
        try:
            intTime = int(time)
        except:
            print_exc()
            return time
        hour = str(intTime / 3600).zfill(2)
        minute = str(intTime % 3600 / 60).zfill(2)
        second = str(intTime % 60).zfill(2)
        if intTime >= 3600:
            return hour + ":" + minute + ":" + second
        else:
            return minute + ":" + second

    @ch.click(C_BUTTON_STOP)
    def click_stop_btn(self):
        xbmc.Player().stop()
        self.isClose = True
        self.isQuit = True

    @ch.click(C_BUTTON_PLAY)
    def click_play_btn(self):
        xbmc.Player().pause()

    @ch.action("left", "*")
    def action_left(self):
        if self.getFocusId() == C_SEEK_SLIDER:
            self.isSeek = True
            self.set_process_status(self.PROGRESS_STATUS - 2)

    @ch.action("right", "*")
    def action_right(self):
        if self.getFocusId() == C_SEEK_SLIDER:
            self.isSeek = True
            self.set_process_status(self.PROGRESS_STATUS + 2)

    @ch.action("back", "*")
    @ch.action("previousmenu", "*")
    def exit_script(self):
        self.isClose = True
