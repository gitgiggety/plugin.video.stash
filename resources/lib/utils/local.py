import xbmcaddon

_ADDON = xbmcaddon.Addon()


def get_localized(id: int) -> str:
    return _ADDON.getLocalizedString(id)
