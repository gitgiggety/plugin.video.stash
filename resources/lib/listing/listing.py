import json
from abc import ABC, abstractmethod
from typing import Optional
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

        xbmcplugin.setPluginCategory(self.handle, title)
        xbmcplugin.setContent(self.handle, 'videos')

        for (item, url) in self._create_items(criterion, sort_field, sort_dir, params):
            xbmcplugin.addDirectoryItem(self.handle, url, item, False)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle)

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
        else:
            item = xbmcgui.ListItem(label=local.get_localized(30007))
            url = utils.get_url(list=self._type)
            items.append((item, url))

        saved_filters = self._client.find_saved_filters(self._filter_type)

        for saved_filter in saved_filters:
            items.append(self._create_item_from_filter(saved_filter))

        return items

    @abstractmethod
    def get_navigation(self) -> [NavigationItem]:
        pass

    @abstractmethod
    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        pass

    @abstractmethod
    def _create_items(self, criterion: dict, sort_field: str, sort_dir: int, params: dict) -> [(xbmcgui.ListItem, str)]:
        pass

    def _create_item(self, scene: dict, **kwargs):
        title = kwargs['title'] if 'title' in kwargs else scene['title']
        screenshot = kwargs['screenshot'] if 'screenshot' in kwargs else scene['paths']['screenshot']
        # * 2 because rating is 1 to 5 and Kodi uses 1 to 10
        rating = scene['rating'] * 2 if 'rating' in scene and scene['rating'] is not None else 0
        duration = int(scene['file']['duration'])
        item = xbmcgui.ListItem(label=title)
        item.setInfo('video', {'title': title,
                               'mediatype': 'video',
                               'plot': scene['details'],
                               'cast': list(map(lambda p: p['name'], scene['performers'])),
                               'duration': duration,
                               'studio': scene['studio']['name'] if scene['studio'] is not None else None,
                               'userrating': rating,
                               'premiered': scene['date'],
                               'tag': list(map(lambda t: t['name'], scene['tags'])),
                               'dateadded': scene['created_at']
                               })

        item.addStreamInfo('video', {'codec': scene['file']['video_codec'],
                                     'width': scene['file']['width'],
                                     'height': scene['file']['height'],
                                     'duration': duration})

        item.addStreamInfo('audio', {'codec': scene['file']['audio_codec']})

        screenshot = self._client.add_api_key(screenshot)
        item.setArt({'thumb': screenshot, 'fanart': screenshot})
        item.setProperty('IsPlayable', 'true')

        return item

    @staticmethod
    def _create_play_url(scene_id: int, **kwargs):
        kwargs['play'] = scene_id
        return utils.get_url(**kwargs)

    def _set_title(self, title: str):
        xbmcplugin.setPluginCategory(self.handle, title)

    def _create_item_from_filter(self, filter: dict, override_title=None) -> [(xbmcgui.ListItem, str)]:
        title = override_title if override_title is not None else filter['name']
        item = xbmcgui.ListItem(label=title)
        filter_data = json.loads(filter['filter'])
        criterion_json = json.dumps(criterion_parser.parse(filter_data['c']))

        url = utils.get_url(list=self._type,
                            title=title,
                            criterion=criterion_json,
                            sort_field=filter_data.get('sortby'),
                            sort_dir=filter_data.get('sortdir')
                            )
        return item, url
