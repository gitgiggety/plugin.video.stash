import json
from abc import ABC, abstractmethod
import xbmcgui
import xbmcplugin

from resources.lib import utils
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


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

    def list_items(self, params: dict = None):
        params = params or {}
        page = int(params.get('page', 1))
        per_page = 100

        (count, items) = self._create_items(page=page, per_page=per_page)
        pages = max(1, -(-count // per_page))

        xbmcplugin.setPluginCategory(self.handle, self._label if pages == 1 else '{} ({})'.format(
            self._label, local.get_localized(30023).format(page, pages)))
        xbmcplugin.setContent(self.handle, 'videos')

        for (item, url) in items:
            xbmcplugin.addDirectoryItem(self.handle, url, item, True)

        if page < pages:
            item = xbmcgui.ListItem(label='{} ({})'.format(local.get_localized(30022),
                                                           local.get_localized(30023).format(page + 1, pages)))
            item.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(self.handle, utils.get_url(**dict(params, page=page + 1)), item, True)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle, updateListing=page > 1)

    @abstractmethod
    def _create_items(self, page: int = 1, per_page: int = 100) -> (int, [(xbmcgui.ListItem, str)]):
        pass

    def _create_item(self, title: str, description: str = '', image_path: str = '', count: int = None,
                     favorite: bool = False) -> xbmcgui.ListItem:
        label = utils.favorite_label(title) if favorite else title
        item = xbmcgui.ListItem(label=label, label2=str(count) if count is not None else '')
        info = item.getVideoInfoTag()
        info.setMediaType('video')
        info.setTitle(label)
        info.setPlot(description or '')
        if count is not None:
            info.setTagLine(local.get_localized(30036).format(count))

        if image_path:
            image = self._client.add_api_key(image_path)
            item.setArt({'thumb': image, 'poster': image})

        return item

    @staticmethod
    def _favorite_menu(kind: str, id, favorite: bool) -> [(str, str)]:
        label = local.get_localized(30040 if favorite else 30039)
        url = utils.get_url(set_favorite=kind, id=id, value=0 if favorite else 1)
        return [(label, 'RunPlugin({})'.format(url))]

    def _create_url(self, title: str, criterion: dict, **kwargs) -> str:
        kwargs['criterion'] = json.dumps(criterion)
        kwargs['list'] = self._browse_for
        kwargs['title'] = title
        return utils.get_url(**kwargs)
