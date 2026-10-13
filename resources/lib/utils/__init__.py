from urllib.parse import urlencode
import xbmcaddon

BASE_URL = ''

PAGE_SIZES = (20, 40, 60, 100)


def get_url(**kwargs):
    return '{}?{}'.format(BASE_URL, urlencode({k: v for k, v in kwargs.items() if v is not None}))


def page_size() -> int:
    try:
        return PAGE_SIZES[int(xbmcaddon.Addon().getSetting('page_size'))]
    except (ValueError, IndexError):
        return 40


def autoplay() -> bool:
    return xbmcaddon.Addon().getSetting('autoplay') == 'true'


def favorite_label(label: str) -> str:
    # Kodi's default fonts have no star glyphs, so favourites are shown in colour
    return '[COLOR gold]{}[/COLOR]'.format(label)


def duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds >= 3600:
        return '{}:{:02d}:{:02d}'.format(seconds // 3600, seconds // 60 % 60, seconds % 60)
    return '{}:{:02d}'.format(seconds // 60, seconds % 60)


def kodi_datetime(iso: str) -> str:
    """Stash RFC 3339 timestamp (2024-06-29T12:34:56+02:00) to Kodi's 2024-06-29 12:34:56"""
    if not iso:
        return ''
    return iso[:19].replace('T', ' ')
