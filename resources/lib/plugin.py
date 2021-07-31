import sys
import json
from urllib.parse import urlencode, parse_qsl
import urllib.parse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import resources.lib.criterion_parser as criterion_parser
from resources.lib.stash_interface import StashInterface

_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
_ADDON = xbmcaddon.Addon()

def get_localized(id):
    return _ADDON.getLocalizedString(id)

browse_types = {
        'scenes': get_localized(30002),
        'performers': get_localized(30003),
        'tags': get_localized(30004),
        'studios': get_localized(30005),
        }

def run():
    global api_key
    global client
    api_key = _ADDON.getSetting('api_key')
    client = StashInterface(_ADDON.getSetting('base_url'), api_key)
    router(sys.argv[2][1:])

def get_url(**kwargs):
    return '{}?{}'.format(_URL, urlencode(kwargs))

def list_root():
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    default_filter = client.findDefaultFilter('SCENES')
    if default_filter != None:
        item, url = create_item_from_filter(default_filter, 'scenes', get_localized(30007))
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)
    else:
        item = xbmcgui.ListItem(label=get_localized(30007))
        url = get_url(browse='scenes', sort_field='date')
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    saved_filters = client.findSavedFilters('SCENES')

    for saved_filter in saved_filters:
        item, url = create_item_from_filter(saved_filter, 'scenes')
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    for type in browse_types:
        item = xbmcgui.ListItem(label=browse_types[type])
        url = get_url(browse=type)
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse(params):
    if params['browse'] == 'scenes':
        browse_scenes(params)
    elif params['browse'] == 'performers':
        browse_performers(params)
    elif params['browse'] == 'tags':
        browse_tags(params)
    elif params['browse'] == 'studios':
        browse_studios(params)

def browse_scenes(params):
    title = params['title'] if 'title' in params else get_localized(30006)

    criterion = json.loads(params['criterion']) if 'criterion' in params else {}
    sort_field = params['sort_field'] if 'sort_field' in params else 'title'
    sort_dir = params['sort_dir'] if 'sort_dir' in params else '0'

    xbmcplugin.setPluginCategory(_HANDLE, title)
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, scenes) = client.findScenes(criterion, sort_field, sort_dir)
    for scene in scenes:
        item = xbmcgui.ListItem(label=scene['title'])
        item.setInfo('video', {'title': scene['title'],
            'mediatype': 'video',
            'plot': scene['details'],
            'cast': list(map(lambda p: p['name'], scene['performers'])),
            'duration': int(scene['file']['duration']),
            'studio': scene['studio']['name'],
            'userrating': scene['rating'] * 2 if 'rating' in scene and scene['rating'] != None else 0, # * 2 because rating is 1 to 5 and Kodi uses 1 to 10
            'premiered': scene['date'],
            'tag': list(map(lambda t: t['name'], scene['tags'])),
            'dateadded': scene['created_at']
        })

        item.addStreamInfo('video', {'codec': scene['file']['video_codec'],
            'width': scene['file']['width'],
            'height': scene['file']['height'],
            'duration': int(scene['file']['duration'])})

        item.addStreamInfo('audio', {'codec': scene['file']['audio_codec']})

        menu = []
        menu.append((_ADDON.getLocalizedString(30008), 'RunPlugin({})'.format(get_url(incrementO='', scene=scene['id']))))
        item.addContextMenuItems(menu)

        screenshot = add_api_key(scene['paths']['screenshot'])
        item.setArt({'thumb': screenshot, 'fanart': screenshot})
        item.setProperty('IsPlayable', 'true')
        url = get_url(play=scene['id'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, False)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_performers(params):
    xbmcplugin.setPluginCategory(_HANDLE, browse_types['performers'])
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, performers) = client.findPerformers()
    for performer in performers:
        item = xbmcgui.ListItem(label=performer['name'])
        item.setInfo('video', {'title': performer['name'],
            'mediatype': 'video',
            'plot': performer['details']})

        item.setArt({'thumb': add_api_key(performer['image_path'])})
        criterion = {'performers': {'modifier': 'INCLUDES_ALL', 'value': [performer['id']]}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=performer['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_tags(params):
    xbmcplugin.setPluginCategory(_HANDLE, browse_types['tags'])
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, tags) = client.findTags()
    for tag in tags:
        item = xbmcgui.ListItem(label=tag['name'])
        item.setInfo('video', {'title': tag['name'],
            'mediatype': 'video'})

        item.setArt({'thumb': add_api_key(tag['image_path'])})
        criterion = {'tags': {'modifier': 'INCLUDES_ALL', 'value': [tag['id']]}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=tag['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_studios(params):
    xbmcplugin.setPluginCategory(_HANDLE, browse_types['studios'])
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, studios) = client.findStudios()
    for studio in studios:
        item = xbmcgui.ListItem(label=studio['name'])
        item.setInfo('video', {'title': studio['name'],
            'mediatype': 'video',
            'plot': studio['details']})

        item.setArt({'thumb': add_api_key(studio['image_path'])})
        criterion = {'studios': {'modifier': 'INCLUDES_ALL', 'value': [studio['id']], 'depth': 0}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=studio['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def create_item_from_filter(filter, type, override_title = None):
    title = override_title if override_title != None else filter['name']
    item = xbmcgui.ListItem(label=title)
    filter_data = json.loads(filter['filter'])
    criterion_json = json.dumps(criterion_parser.parse(filter_data['c']))

    url = get_url(browse='scenes', title=title, criterion=criterion_json, sort_field=filter_data['sortby'], sort_dir=filter_data['disp'])
    return (item, url)

def play(params):
    scene = client.findScene(params['play'])
    item = xbmcgui.ListItem(path=scene['paths']['stream'])
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=item)

def incrementO(params):
    if 'scene' in params:
        oCount = client.sceneIncrementO(params['scene'])
        xbmc.executebuiltin('Notification(Stash, {} {})'.format(get_localized(30009), oCount))


def router(paramstring):
    params = dict(parse_qsl(paramstring, keep_blank_values=True))

    if params:
        if 'browse' in params:
            browse(params)
        elif 'play' in params:
            play(params)
        elif 'incrementO' in params:
            incrementO(params)
    else:
        list_root()

def add_api_key(url):
    if api_key:
        url = "{}{}apikey={}".format(url, '&' if '?' in url else '?', urllib.parse.quote(api_key))

    return url

