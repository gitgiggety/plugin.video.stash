from typing import Optional

from .listing import Listing
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local
from ..navigation import NavigationItem, PerformerItem, TagItem


class SceneMarkerListing(Listing):
    def __init__(self, client: StashInterface):
        Listing.__init__(self, client, 'scene_markers', local.get_localized(30010), filter_type='SCENE_MARKERS')

    def get_navigation(self) -> [NavigationItem]:
        return [
            PerformerItem(self._client, 'scene_markers'),
            TagItem(self._client, 'scene_markers'),
            TagItem(self._client, 'scene_markers', type='scene_tags', label=local.get_localized(30012)),
        ]

    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        browse = params['browse']
        if browse == 'performers':
            return PerformerItem(self._client, 'scene_markers')
        if browse == 'tags':
            return TagItem(self._client, 'scene_markers')
        if browse == 'scene_tags':
            return TagItem(self._client, 'scene_markers', type='scene_tags', label=local.get_localized(30012))

    def _create_items(self, criterion: dict, sort_field: str, sort_dir: int, params: dict):
        if 'scene' in params:
            scene = self._client.find_scene(params['scene'])

            self._set_title('{} {}'.format(local.get_localized(30011), scene['title']))
            markers = scene['scene_markers']
        else:
            (_, markers) = self._client.find_scene_markers(criterion, sort_field, sort_dir)

        items = []
        for marker in markers:
            title = '{} - {}'.format(marker['title'], marker['primary_tag']['name'])
            item = self._create_item(marker['scene'], title=title, screenshot=marker['screenshot'])
            url = self._create_play_url(marker['scene']['id'])

            duration = marker['scene']['file']['duration']
            item.setProperty('StartPercent', str(round(marker['seconds'] / duration * 100, 2)))

            items.append((item, url))

        return items
