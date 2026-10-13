import json
import os.path
from abc import ABC, abstractmethod
from typing import Optional
import xbmc
import xbmcgui
import xbmcplugin

from resources.lib import utils, criterion_parser
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local
from resources.lib.navigation import NavigationItem


class Listing(ABC):
    handle: int

    def __init__(self, client: StashInterface, type: str, label: str, **kwargs):
        self._client = client
        self._type = type
        self._label = label
        self._filter_type = kwargs['filter_type'] if 'filter_type' in kwargs else None

    def list_items(self, params: dict):
        title = params['title'] if 'title' in params else self._label

        criterion = json.loads(params['criterion']) if 'criterion' in params else {}
        sort_field = params['sort_field'] if 'sort_field' in params else None
        sort_dir = params['sort_dir'] if 'sort_dir' in params else 'asc'
        page = int(params.get('page', 1))
        per_page = utils.page_size()

        (count, items) = self._create_items(criterion, sort_field, sort_dir, params, page=page, per_page=per_page)
        pages = max(1, -(-count // per_page))

        xbmcplugin.setPluginCategory(self.handle, title if pages == 1 else '{} ({})'.format(
            title, local.get_localized(30023).format(page, pages)))
        xbmcplugin.setContent(self.handle, 'videos')

        for (item, url) in items:
            xbmcplugin.addDirectoryItem(self.handle, url, item, False)

        if page < pages:
            next_params = dict(params, page=page + 1)
            item = xbmcgui.ListItem(label='{} ({})'.format(local.get_localized(30022),
                                                           local.get_localized(30023).format(page + 1, pages)))
            item.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(self.handle, utils.get_url(**next_params), item, True)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle, updateListing=page > 1)

    def get_root_item(self, override_title: str = "") -> (xbmcgui.ListItem, str):
        item = xbmcgui.ListItem(label=override_title if override_title != "" else self._label)
        url = utils.get_url(list=self._type)

        return item, url

    def get_filters(self) -> [(xbmcgui.ListItem, str)]:
        if self._filter_type is None:
            return []

        items = []
        default_filter = self._client.find_default_filter(self._filter_type)
        if default_filter is not None:
            items.append(self._create_item_from_filter(default_filter, local.get_localized(30007)))

        saved_filters = self._client.find_saved_filters(self._filter_type)

        for saved_filter in saved_filters or []:
            items.append(self._create_item_from_filter(saved_filter))

        return items

    def sort_options(self) -> [(str, str, str)]:
        """(label, sort field, default direction) offered in the "Sort by" dialog"""
        return []

    @abstractmethod
    def get_navigation(self) -> [NavigationItem]:
        pass

    @abstractmethod
    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        pass

    @abstractmethod
    def _create_items(self, criterion: dict, sort_field: str, sort_dir: str, params: dict,
                      page: int = 1, per_page: int = 40) -> (int, [(xbmcgui.ListItem, str)]):
        pass

    @staticmethod
    def scene_title(scene: dict) -> str:
        if scene.get('title'):
            return scene['title']
        if scene.get('files'):
            return os.path.splitext(scene['files'][0]['basename'])[0]
        return scene['id']

    def _create_item(self, scene: dict, **kwargs):
        title = kwargs['title'] if 'title' in kwargs else self.scene_title(scene)
        screenshot = kwargs['screenshot'] if 'screenshot' in kwargs else scene['paths']['screenshot']
        file = scene['files'][0] if scene['files'] else {}
        duration = int(file.get('duration') or 0)

        item = xbmcgui.ListItem(label=title)
        info = item.getVideoInfoTag()
        info.setMediaType('video')
        info.setTitle(title)
        info.setPlot(scene['details'] or '')
        info.setCast([xbmc.Actor(p['name'], thumbnail=self._client.add_api_key(p.get('image_path')) or '')
                      for p in scene['performers']])
        info.setDuration(duration)
        info.setPlaycount(scene.get('play_count') or 0)
        if scene['studio'] is not None:
            info.setStudios([scene['studio']['name']])
        # / 10 because rating is 1 to 100 and Kodi uses 1 to 10
        info.setUserRating(round((scene.get('rating100') or 0) / 10))
        if scene['date']:
            info.setPremiered(scene['date'])
            info.setYear(int(scene['date'][:4]))
        info.setTags([t['name'] for t in scene['tags']])
        info.setDateAdded(utils.kodi_datetime(scene['created_at']))
        info.setLastPlayed(utils.kodi_datetime(scene.get('last_played_at')))
        info.setResumePoint(float(scene.get('resume_time') or 0), float(duration))
        if file:
            info.addVideoStream(xbmc.VideoStreamDetail(width=file['width'], height=file['height'],
                                                       codec=file['video_codec'] or '', duration=duration))
            info.addAudioStream(xbmc.AudioStreamDetail(codec=file['audio_codec'] or ''))

        screenshot = self._client.add_api_key(screenshot)
        art_dict = {'thumb': screenshot, 'fanart': screenshot}
        if scene['studio'] and scene['studio'].get('image_path'):
            art_dict["banner"] = self._client.add_api_key(scene["studio"]["image_path"])
        item.setArt(art_dict)
        item.setProperty('IsPlayable', 'true')

        return item

    def create_queue_item(self, scene: dict) -> xbmcgui.ListItem:
        item = self._create_item(scene)
        # The resume point is applied by the service when chosen in play_from
        item.getVideoInfoTag().setResumePoint(0.0)
        return item

    def _context_menu(self, params: dict) -> [(str, str)]:
        if not self.sort_options():
            return []
        sort_params = dict(params, choose_sort=self._type)
        return [(local.get_localized(30024), 'RunPlugin({})'.format(utils.get_url(**sort_params)))]

    @staticmethod
    def _create_play_url(scene_id: int, **kwargs):
        kwargs['play'] = scene_id
        return utils.get_url(**kwargs)

    def _set_title(self, title: str):
        xbmcplugin.setPluginCategory(self.handle, title)

    def _create_item_from_filter(self, filter: dict, override_title=None) -> [(xbmcgui.ListItem, str)]:
        title = override_title if override_title is not None else filter['name']
        item = xbmcgui.ListItem(label=title)
        find_filter = filter['find_filter'] or {}
        object_filter = filter['object_filter'] or {}
        criterion_json = json.dumps(criterion_parser.parse(object_filter))

        url = utils.get_url(list=self._type,
                            title=title,
                            criterion=criterion_json,
                            sort_field=find_filter.get('sort'),
                            sort_dir=find_filter.get('direction')
                            )
        return item, url
