# -*- coding: utf8 -*-

import os
import urllib
import xbmc
import xbmcaddon
import xbmcgui
try:
    import simplejson
except:
    import json as simplejson
import threading
import time
from functools import wraps

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
HOME = xbmcgui.Window(10000)
SETTING = ADDON.getSetting


class MWT(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}

    def __init__(self, timeout=2):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                data = simplejson.dumps(v)
                data = data[1:-17]
                if data == '{"status": "Fail"}':
                    print 'get data failed'
                    raise KeyError
                print "cache"
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                print "new"
                v = self.cache[key] = f(*args, **kwargs), time.time()
            return v[0]
        func.func_name = f.func_name

        return func


class GlobalProperty(object):
    """global property"""
    _items = dict()

    @staticmethod
    def set(key, value):
        GlobalProperty._items[key] = value

    @staticmethod
    def clear(key):
        if key in GlobalProperty._items:
            del GlobalProperty._items[key]

    @staticmethod
    def get(key):
        if key in GlobalProperty._items:
            return GlobalProperty._items[key]
        else:
            return None

    @staticmethod
    def clearAll():
        GlobalProperty._items = dict()


class InterruptableThread(threading.Thread):

    def __init__(self, function_array):
        super(InterruptableThread, self).__init__()
        self.function_array = function_array
        self.stoprequest = threading.Event()

    def run(self):
        for function in self.function_array:
            if not self.stoprequest.isSet():
                try:
                    function()
                except:
                    log("Exception in %s" % function.__name__)
            else:
                break
        return True

    def stop(self):
        self.stoprequest.set()

    def join(self, timeout=None):
        self.stoprequest.set()
        super(InterruptableThread, self).join(timeout)


def run_async(func):
    """
    Decorator to run a function in a separate thread
    """
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = threading.Thread(target=func,
                                   args=args,
                                   kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


def download(url, target):
    try:
        urllib.urlretrieve(url, target)
        return True
    except:
        return False


def busy_dialog(func):
    """
    Decorator to show busy dialog while function is running
    Only one of the decorated functions may run simultaniously
    """

    @wraps(func)
    def decorator(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        result = func(self, *args, **kwargs)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        return result

    return decorator


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8", 'ignore')
    message = u'%s: %s' % (ADDON_ID, txt)
    xbmc.log(msg=message.encode("utf-8", 'ignore'),
             level=xbmc.LOGDEBUG)


def notify(header="", message="", icon=ADDON_ICON, display_time=5000, sound=True):
    xbmcgui.Dialog().notification(heading=header,
                                  message=message,
                                  icon=icon,
                                  time=display_time,
                                  sound=sound)


def get_kodi_json(method, params):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "%s", "params": %s, "id": 1}' % (method, params))
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    return simplejson.loads(json_query)


def prettyprint(string):
    log(simplejson.dumps(string,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')))


def colorize(label, color):
    return "[COLOR %s]%s[/COLOR]" % (color, label)


def create_listitems(data=None):
    if not data:
        return []
    itemlist = []
    for (count, result) in enumerate(data):
        listitem = xbmcgui.ListItem('%s' % (str(count)))
        for (key, value) in result.iteritems():
            if not value:
                continue
            value = unicode(value)
            if key.lower() in ["name", "label"]:
                listitem.setLabel(value)
            elif key.lower() in ["label2"]:
                listitem.setLabel2(value)
            elif key.lower() in ["title"]:
                listitem.setLabel(value)
                listitem.setInfo('video', {key.lower(): value})
            elif key.lower() in ["thumb"]:
                listitem.setThumbnailImage(value)
                listitem.setArt({key.lower(): value})
            elif key.lower() in ["icon"]:
                listitem.setIconImage(value)
                listitem.setArt({key.lower(): value})
            elif key.lower() in ["path"]:
                listitem.setPath(path=value)
            elif key.lower() in ["poster", "banner", "fanart"]:
                listitem.setArt({key.lower(): value})
            # else:
            listitem.setProperty('%s' % (key), value)
        listitem.setProperty("index", str(count))
        itemlist.append(listitem)
    return itemlist


def okDialog(line1='获取数据失败 请检查网络', title='提示', line2=None, line3=None):
    dialog = xbmcgui.Dialog()
    dialog.ok(title, line1, line2, line3)


def format_time(time, ToChinese=False):
    try:
        intTime = int(time)
    except:
        return time
    hour = str(intTime / 3600).zfill(2)
    minute = str(intTime % 3600 / 60).zfill(2)
    second = str(intTime % 60).zfill(2)
    if intTime >= 3600:
        if not ToChinese:
            return hour + ":" + minute + ":" + second
        return hour + u"小时" + minute + u"分" + second + u"秒"
    else:
        if not ToChinese:
            return minute + ":" + second
        return minute + u"分" + second + u"秒"


def SecondtoYMD(secTime):
    return str(time.strftime('%Y-%m-%d', time.localtime(secTime))).replace(":", "")


def stop_play():
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()
