import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_SETTING = ADDON.getSetting
ADDRESS_FILE = "/sys/class/net/eth0/address"


class Device(object):

    @classmethod
    def get_device_id(cls):
        try:
            return Device.ID
        except:
            xbmc.log("device id doesn't exit")
            if ADDON_SETTING("device-id") != "":
                return ADDON_SETTING("device-id")
            else:
                if xbmc.getCondVisibility('system.platform.Android'):
                    Device.ID = cls.get_mac_from_addressinfo().replace(":", "")[-6:]
                    return Device.ID
                else:
                    import uuid
                    node = uuid.getnode()
                    mac_addess = uuid.UUID(int=node).hex[-12:]
                    Device.ID = mac_addess[-6:]
                    return Device.ID

    @classmethod
    def get_mac_from_addressinfo(cls):
        with open(ADDRESS_FILE) as file:
            mac = file.read().strip()
        return mac
