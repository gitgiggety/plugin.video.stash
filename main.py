import json
import sys
from urllib.parse import urlencode, parse_qsl
import xbmcaddon
import xbmcgui
import xbmcplugin
from stash_interface import StashInterface
import criterion_parser

_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
_ADDON = xbmcaddon.Addon()

browse_types = {
        'scenes': 'All',
        'performers': 'Performers',
        'tags': 'Tags',
        'studios': 'Studios',
        }

def get_url(**kwargs):
    return '{}?{}'.format(_URL, urlencode(kwargs))

def list_root():
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    saved_filters = client.findSavedFilters('SCENES')

    for saved_filter in saved_filters:
        item = xbmcgui.ListItem(label=saved_filter['name'])
        filter_data = json.loads(saved_filter['filter'])
        criterion_json = json.dumps(criterion_parser.parse(filter_data['c']))

        url = get_url(browse='scenes', title=saved_filter['name'], criterion=criterion_json, sort_field=filter_data['sortby'], sort_dir=filter_data['disp'])
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
    title = params['title'] if 'title' in params else 'Scenes'

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
            'studio': scene['studio']['name']})

        item.setArt({'thumb': scene['paths']['screenshot'], 'fanart': scene['paths']['screenshot']})
        item.setProperty('IsPlayable', 'true')
        url = get_url(play=scene['id'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, False)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_performers(params):
    xbmcplugin.setPluginCategory(_HANDLE, 'Performers')
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, performers) = client.findPerformers()
    for performer in performers:
        item = xbmcgui.ListItem(label=performer['name'])
        item.setInfo('video', {'title': performer['name'],
            'mediatype': 'video',
            'plot': performer['details']})

        item.setArt({'thumb': performer['image_path']})
        criterion = {'performers': {'modifier': 'INCLUDES_ALL', 'value': [performer['id']]}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=performer['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_tags(params):
    xbmcplugin.setPluginCategory(_HANDLE, 'Tags')
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, tags) = client.findTags()
    for tag in tags:
        item = xbmcgui.ListItem(label=tag['name'])
        item.setInfo('video', {'title': tag['name'],
            'mediatype': 'video'})

        item.setArt({'thumb': tag['image_path']})
        criterion = {'tags': {'modifier': 'INCLUDES_ALL', 'value': [tag['id']]}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=tag['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def browse_studios(params):
    xbmcplugin.setPluginCategory(_HANDLE, 'Studios')
    xbmcplugin.setContent(_HANDLE, 'videos')

    (count, studios) = client.findStudios()
    for studio in studios:
        item = xbmcgui.ListItem(label=studio['name'])
        item.setInfo('video', {'title': studio['name'],
            'mediatype': 'video',
            'plot': studio['details']})

        item.setArt({'thumb': studio['image_path']})
        criterion = {'studios': {'modifier': 'INCLUDES_ALL', 'value': [studio['id']], 'depth': 0}}
        url = get_url(browse='scenes', criterion=json.dumps(criterion), title=studio['name'])
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def play(params):
    scene = client.findScene(params['play'])
    item = xbmcgui.ListItem(path=scene['paths']['stream'])
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=item)

def router(paramstring):
    params = dict(parse_qsl(paramstring))

    if params:
        if 'browse' in params:
            browse(params)
        elif 'play' in params:
            play(params)
    else:
        list_root()

if __name__ == '__main__':
    client = StashInterface(_ADDON.getSetting('base_url'))
    router(sys.argv[2][1:])
