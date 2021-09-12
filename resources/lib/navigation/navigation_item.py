import json
from abc import ABC, abstractmethod
import xbmcgui
import xbmcplugin

from resources.lib import utils
from resources.lib.stash_interface import StashInterface


class NavigationItem(ABC):
    handle: int

    def __init__(self, client: StashInterface, type: str, label: str, browse_for: str):
        self._client = client
        self._type = type
        self._browse_for = browse_for
        self._label = label

    def get_root_item(self) -> (xbmcgui.ListItem, str):
        item = xbmcgui.ListItem(label=self._label)
        url = utils.get_url(browse=self._type, browse_for=self._browse_for)

        return item, url

    def list_items(self):
        xbmcplugin.setPluginCategory(self.handle, self._label)
        xbmcplugin.setContent(self.handle, 'videos')

        for (item, url) in self._create_items():
            xbmcplugin.addDirectoryItem(self.handle, url, item, True)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle)

    @abstractmethod
    def _create_items(self) -> [(xbmcgui.ListItem, str)]:
        pass

    def _create_item(self, title: str, description: str = '', image_path: str = '') -> xbmcgui.ListItem:
        item = xbmcgui.ListItem(label=title)
        item.setInfo('video', {'title': title,
                               'mediatype': 'video',
                               'plot': description})

        if image_path != '':
            item.setArt({'thumb': self._client.add_api_key(image_path)})

        return item

    def _create_url(self, title: str, criterion: dict, **kwargs) -> str:
        kwargs['criterion'] = json.dumps(criterion)
        kwargs['list'] = self._browse_for
        kwargs['title'] = title
        return utils.get_url(**kwargs)
