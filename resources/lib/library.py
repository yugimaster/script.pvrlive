#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
from pvr import EPGAPI
from traceback import print_exc
try:
    import StorageServer2
except:
    import storageserverdummy as StorageServer2
try:
    import simplejson
except:
    import json as simplejson


class LibraryFunctions():

    storageStack = {}

    def __init__(self):
        pass

    def _get_data(self, data_type, key=None, time=5):
        if data_type in self.storageStack:
            cache = self.storageStack[data_type]
        else:
            cache = StorageServer2.TimedStorage(data_type, time)
            self.storageStack[data_type] = cache
        if key is None:
            key = data_type
        try:
            _data = cache[key]
            print "-------GOT CACHE--------TYPE:" + data_type + " KEY:" + str(key)
            return _data
        except:
            print "--Error--GOT CACHE--------TYPE:" + data_type + " KEY:" + str(key)
            return None

    def _set_data(self, data_type, data, key=None, time=5):
        if data_type in self.storageStack:
            cache = self.storageStack[data_type]
        else:
            cache = StorageServer2.TimedStorage(data_type, time)
            self.storageStack[data_type] = cache
        if key is None:
            key = data_type
        cache[key] = data

    def fetch_pvr_channel_list(self, columnid="9"):
        data = EPGAPI.get_pvr_channel_list(columnid)
        if simplejson.dumps(data) == '{"status": "Fail"}' or data is None:
            return None
        return data
