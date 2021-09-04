from typing import Optional

from .listing import Listing
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local
from ..navigation import NavigationItem


class SceneMarkerListing(Listing):
    def __init__(self, client: StashInterface):
        Listing.__init__(self, client, 'scene_markers', local.get_localized(30010), filter_type='SCENE_MARKERS')

    def get_navigation(self) -> [NavigationItem]:
        return []

    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        return None

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
            item = self._create_item(marker['scene'], title)
            url = self._create_play_url(marker['scene']['id'])

            duration = marker['scene']['file']['duration']
            item.setProperty('StartPercent', str(round(marker['seconds'] / duration * 100, 2)))

            items.append((item, url))

        return items
