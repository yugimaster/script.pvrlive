#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import urllib
import urllib2
import json
import hashlib
from traceback import print_exc
from Utils import *
from device import Device
try:
    import simplejson
except:
    import json as simplejson


def make_qs(**params):
    return urllib.urlencode(params)


def GetHttpData(url, data=None, cookie=None, headers=None):
    xbmc.log("Fetch URL :%s, with data: %s" % (url, data))
    try:
        req = urllib2.Request(url)
        if cookie is not None:
            req.add_header('Cookie', cookie)
        if headers is not None:
            for headers in headers:
                req.add_header(headers, headers[headers])
        if data:
            response = urllib2.urlopen(req, data, timeout=3)
        else:
            response = urllib2.urlopen(req, timeout=3)
        httpdata = response.read()
        response.close()
    except urllib2.URLError, e:
        xbmc.log("URLError: " + str(e.reason))
        if str(e.reason) == 'getaddrinfo returns an empty list':
            httpdata = '{"status": "networkoff"}'
        elif str(e.reason) == '[Errno 11001] getaddrinfo failed':
            httpdata = '{"status": "networkoff"}'
        else:
            httpdata = '{"status": "Fail"}'
    except:
        print_exc()
        httpdata = '{"status": "Fail"}'
    return httpdata


class OISAPI():

    SERVER = "http://ocsgh01.mxott.com:5000"

    def __init__(self):
        pass


class EPGAPI(object):

    SERVER = "http://epggh01.mxott.com:8080"
    OISAPI = OISAPI()
    TOKEN = "guoziyun"

    @classmethod
    def get_pvr_channel_list(cls, columnid="9"):
        """get pvr channel list with columnid

        Returns:
            JSON-String: the result
        """
        API = "/epgs/tvmovie/media/get"
        data = cls()._get(API, columnid=columnid)
        return data

    @classmethod
    def get_live_play(cls, sid, mop_url):
        if mop_url != "":
            url_id = mop_url[6:]
        else:
            url_id = sid
        url = cls.OISAPI.SERVER + "/" + url_id + ".m3u8?"
        tid = Device.get_device_id()
        user = tid
        data = url + make_qs(protocol="hls", user=user, tid=tid, sid=sid, type="stb", token=cls.TOKEN)
        return data

    def _get(self, API, **param):
        data = QueryParams(API, **param)
        data = GetHttpData(self.SERVER + API + "?" + urllib.urlencode(data))
        s = simplejson.loads(data)
        xbmc.log(json.dumps(s, sort_keys=True,
                 indent=4, separators=(',', ': ')))
        try:
            return s
        except:
            return None

    def _post(self, API, **param):
        data = QueryParams(API, **param)
        data = GetHttpData(self.SERVER + API, urllib.urlencode(data), headers=data)
        try:
            return simplejson.loads(data)
        except:
            return None


class QueryParams(dict):
    BASE_PARA = {"token": "guoziyun"}

    def __init__(self, API, **arg):
        self._update(self.BASE_PARA)
        self._update(arg)
        self._sign(API)

    def _update(self, dict):
        for k, v in dict.items():
            self[k] = v

    def _sign(self, API):
        preurl = API + "?"
        od = [(k, self[k]) for k in sorted(self.keys())]
        preurl += urllib.urlencode(od, True)
        m = hashlib.md5()
        m.update(preurl)
