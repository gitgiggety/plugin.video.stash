import datetime
import json
import random
import sys
from urllib.parse import parse_qsl
from typing import Optional
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib import utils
from resources.lib.listing import create_listing, Listing, SceneListing
from resources.lib.navigation import NavigationItem, PerformerItem, TagItem
from resources.lib.service import PLAYING_PROPERTY, START_OFFSET_PROPERTY
from resources.lib.stash_interface import StashInterface

utils.BASE_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
NavigationItem.handle = _HANDLE
Listing.handle = _HANDLE
_ADDON = xbmcaddon.Addon()
api_key: str = ''
client: Optional[StashInterface] = None

res_map = {
    "Original": "",
    "4k": "FOUR_K",
    "1440p": "QUAD_HD",
    "FHD": "FULL_HD",
    "720p": "STANDARD_HD",
    "SD": "STANDARD",
    "240p": "LOW",
}

res_height_map = {
    "4k": 1920,
    "1440p": 1440,
    "FHD": 1080,
    "720p": 720,
    "SD": 480,
    "240p": 240,
}


def run():
    global api_key
    global client
    global playback_res
    api_key = _ADDON.getSetting('api_key')
    client = StashInterface(_ADDON.getSetting('base_url'), api_key)
    playback_res = res_map.get(_ADDON.getSetting('res'), "")
    router(sys.argv[2][1:])


def _folder(label: str, url: str, icon: str = 'DefaultFolder.png', is_folder: bool = True):
    item = xbmcgui.ListItem(label=label)
    item.setArt({'icon': icon})
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, is_folder)


def browse_root():
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    loc = utils.local.get_localized
    _folder(loc(30016), utils.get_url(search='scenes'), 'DefaultAddonsSearch.png', is_folder=False)
    _folder(loc(30017), utils.get_url(list='scenes', title=loc(30017), sort_field='created_at', sort_dir='desc'),
            'DefaultRecentlyAddedMovies.png')
    _folder(loc(30018), utils.get_url(list='scenes', title=loc(30018), sort_field='last_played_at', sort_dir='desc',
                                      criterion=json.dumps({'resume_time': {'modifier': 'GREATER_THAN', 'value': 0}})),
            'DefaultInProgressShows.png')
    _folder(loc(30019), utils.get_url(list='scenes', title=loc(30019), sort_field='last_played_at', sort_dir='desc',
                                      criterion=json.dumps({'play_count': {'modifier': 'GREATER_THAN', 'value': 0}})),
            'DefaultRecentlyAddedEpisodes.png')
    _folder(loc(30020), utils.get_url(list='scenes', title=loc(30020), sort_field=random_sort()))
    for favorites in (PerformerItem(client, 'scenes', favorites=True), TagItem(client, 'scenes', favorites=True)):
        (item, url) = favorites.get_root_item()
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    listing = SceneListing(client)
    for (item, url) in listing.get_filters():
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    (item, url) = listing.get_root_item(loc(30002))
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    for navItem in listing.get_navigation():
        (item, url) = navItem.get_root_item()
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    item = xbmcgui.ListItem(label=loc(30010))
    url = utils.get_url(browse='scene_markers')
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)


def browse(params):
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    listing = create_listing(params['browse'], client)
    for (item, url) in listing.get_filters():
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    (item, url) = listing.get_root_item(utils.local.get_localized(30002))
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    for navItem in listing.get_navigation():
        (item, url) = navItem.get_root_item()
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)


def list_items(params: dict):
    listing = create_listing(params['list'], client)
    listing.list_items(params)


def browse_for(params: dict):
    listing = create_listing(params['browse_for'], client)
    navigation = listing.get_navigation_item(params)
    navigation.list_items(params)


def random_sort() -> str:
    # A seed keeps the order stable while paging, like the random sort in Stash' UI
    return 'random_{}'.format(random.randint(0, 99999999))


def search(params: dict):
    loc = utils.local.get_localized
    query = xbmcgui.Dialog().input(loc(30037))
    if query:
        url = utils.get_url(list=params['search'], q=query, title='{}: {}'.format(loc(30016), query),
                            sort_field='date', sort_dir='desc')
        xbmc.executebuiltin('Container.Update({})'.format(url))


def choose_sort(params: dict):
    listing = create_listing(params.pop('choose_sort'), client)
    options = listing.sort_options()
    labels = [label for (label, _, _) in options] + [utils.local.get_localized(30033)]
    choice = xbmcgui.Dialog().select(utils.local.get_localized(30024), labels)
    if choice < 0:
        return

    params.pop('page', None)
    if choice == len(options):
        params['sort_dir'] = 'asc' if params.get('sort_dir', 'asc').lower() == 'desc' else 'desc'
    else:
        (_, field, direction) = options[choice]
        params['sort_field'] = random_sort() if field == 'random' else field
        params['sort_dir'] = direction

    xbmc.executebuiltin('Container.Update({},replace)'.format(utils.get_url(**params)))


def play_from(params: dict):
    loc = utils.local.get_localized
    scene_id = params.pop('play_from')
    listing = SceneListing(client)
    scenes = listing.queue(params, scene_id, utils.page_size())

    resume = float(scenes[0].get('resume_time') or 0)
    if resume > 0:
        choice = xbmcgui.Dialog().contextmenu(
            ['{} {}'.format(loc(30047), utils.duration(resume)), loc(30048)])
        if choice < 0:
            return
        if choice == 0:
            xbmcgui.Window(10000).setProperty(START_OFFSET_PROPERTY, '{}:{}'.format(scene_id, resume))

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for scene in scenes:
        item = listing.create_queue_item(scene)
        playlist.add(Listing._create_play_url(scene['id']), item)
    xbmc.Player().play(playlist)


def get_mp4_stream(sceneStreams: dict) -> str:
    for stream in sceneStreams:
        if stream["label"] == "DASH":
            return stream


def play(params: dict):
    scene = client.find_scene(params['play'])
    item = xbmcgui.ListItem()
    if playback_res != "" and scene["files"][0]["height"] > res_height_map[_ADDON.getSetting('res')]:
        stream = get_mp4_stream(scene["sceneStreams"])
        url = stream["url"].replace("ORIGINAL", playback_res)
        item.setMimeType('application/xml+dash')
        item.setContentLookup(False)

        item.setProperty('inputstream', 'inputstream.adaptive')
        item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        item.setProperty('inputstream.adaptive.stream_headers',
                         f'apikey={api_key}')
        item.setProperty('inputstream.adaptive.manifest_headers',
                         f'apikey={api_key}')
        item.setPath(url)
    else:
        streamurl = scene['paths']['stream']
        item.setPath(streamurl)

    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=item)


def increment_o(params: dict):
    # Without a scene: the scene currently playing, so this can be bound to a key, e.g. in a keymap:
    # <key>RunPlugin(plugin://plugin.video.stash/?increment_o)</key>
    scene = params.get('scene') or xbmcgui.Window(10000).getProperty(PLAYING_PROPERTY)
    if scene:
        o_count = client.scene_add_o(scene)
        xbmc.executebuiltin('Notification(Stash, {} {})'.format(utils.local.get_localized(30009), o_count))


def set_favorite(params: dict):
    client.set_favorite(params['set_favorite'], params['id'], params.get('value') == '1')
    xbmc.executebuiltin('Container.Refresh')


def rate_scene(params: dict):
    loc = utils.local.get_localized
    labels = [loc(30043), loc(30050)] + [loc(30051).format(stars) for stars in range(2, 6)]
    current = round(int(params.get('rating') or 0) / 20)
    choice = xbmcgui.Dialog().select(loc(30041), labels, preselect=current)
    if choice >= 0:
        client.set_scene_rating(params['rate_scene'], choice * 20 if choice else None)
        xbmc.executebuiltin('Container.Refresh')


def scene_performers(params: dict):
    loc = utils.local.get_localized
    performers = client.find_scenes({'id': {'modifier': 'EQUALS', 'value': int(params['scene_performers'])}},
                                    per_page=1)[1][0]['performers']
    labels = ['{} ({})'.format(utils.favorite_label(p['name']), loc(30052)) if p['favorite'] else p['name']
              for p in performers]
    choice = xbmcgui.Dialog().select(loc(30042), labels)
    if choice < 0:
        return
    performer = performers[choice]
    actions = [loc(30053), loc(30054), loc(30040 if performer['favorite'] else 30039)]
    action = xbmcgui.Dialog().contextmenu(actions)
    if action == 0:
        xbmc.executebuiltin('Container.Update({})'.format(performer_scenes_url(performer['id'], performer['name'])))
    elif action == 1:
        performer_info({'performer_info': performer['id']})
    elif action == 2:
        favorite = client.set_favorite('performer', performer['id'], not performer['favorite'])
        xbmc.executebuiltin('Notification(Stash, {}: {})'.format(performer['name'], loc(30045 if favorite else 30046)))


def performer_info(params: dict):
    loc = utils.local.get_localized
    performer = client.find_performer(params['performer_info'])
    birthdate = performer.get('birthdate')
    if birthdate:
        born = birthdate
        if not performer.get('death_date'):
            today = datetime.date.today()
            (year, month, day) = (int(part) for part in birthdate.split('-'))
            born = '{} ({})'.format(birthdate, today.year - year - ((today.month, today.day) < (month, day)))
    else:
        born = None
    facts = [
        (30055, ', '.join(performer.get('alias_list') or [])),
        (30056, born),
        (30057, performer.get('death_date')),
        (30058, performer.get('country')),
        (30059, performer.get('ethnicity')),
        (30060, performer.get('hair_color')),
        (30061, performer.get('eye_color')),
        (30062, '{} cm'.format(performer['height_cm']) if performer.get('height_cm') else None),
        (30063, performer.get('measurements')),
        (30064, performer.get('career_length')),
        (30065, performer.get('tattoos')),
        (30066, performer.get('piercings')),
        (30006, performer.get('scene_count')),
    ]
    lines = ['[B]{}:[/B] {}'.format(loc(label), value) for (label, value) in facts if value]
    plot = '\n'.join(lines)
    if performer.get('details'):
        plot = '{}\n\n{}'.format(plot, performer['details'])

    name = performer['name']
    if performer.get('disambiguation'):
        name = '{} ({})'.format(name, performer['disambiguation'])
    item = xbmcgui.ListItem(label=name)
    info = item.getVideoInfoTag()
    info.setMediaType('video')
    info.setTitle(name)
    info.setPlot(plot)
    info.setGenres([tag['name'] for tag in performer.get('tags') or []])
    info.setUserRating(round((performer.get('rating100') or 0) / 10))
    if performer.get('country'):
        info.setCountries([performer['country']])
    image = client.add_api_key(performer.get('image_path'))
    if image:
        item.setArt({'thumb': image, 'poster': image})
    xbmcgui.Dialog().info(item)


def performer_scenes_url(performer_id, name: str) -> str:
    criterion = {'performers': {'modifier': 'INCLUDES_ALL', 'value': [performer_id]}}
    return utils.get_url(list='scenes', title=name, criterion=json.dumps(criterion), sort_field='date',
                         sort_dir='desc')


def router(param_string: str):
    params = dict(parse_qsl(param_string, keep_blank_values=True))

    if params:
        if 'play_from' in params:
            play_from(params)
        elif 'choose_sort' in params:
            choose_sort(params)
        elif 'search' in params:
            search(params)
        elif 'browse_for' in params:
            browse_for(params)
        elif 'browse' in params:
            browse(params)
        elif 'list' in params:
            list_items(params)
        elif 'play' in params:
            play(params)
        elif 'increment_o' in params:
            increment_o(params)
        elif 'set_favorite' in params:
            set_favorite(params)
        elif 'rate_scene' in params:
            rate_scene(params)
        elif 'scene_performers' in params:
            scene_performers(params)
        elif 'performer_info' in params:
            performer_info(params)
    else:
        browse_root()
