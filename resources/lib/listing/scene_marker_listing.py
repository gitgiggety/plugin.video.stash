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

    def sort_options(self):
        return [
            (local.get_localized(30025), 'title', 'asc'),
            (local.get_localized(30026), 'created_at', 'desc'),
            (local.get_localized(30020), 'random', 'asc'),
        ]

    def _create_items(self, criterion: dict, sort_field: str, sort_dir: str, params: dict, page=1, per_page=40):
        if 'scene' in params:
            scene = self._client.find_scene(params['scene'])

            self._set_title('{} {}'.format(local.get_localized(30011), self.scene_title(scene)))
            markers = scene['scene_markers']
            count = len(markers)
        else:
            (count, markers) = self._client.find_scene_markers(criterion, sort_field, sort_dir, page=page,
                                                               per_page=per_page, q=params.get('q'))

        sort_menu = [] if 'scene' in params else self._context_menu(params)
        items = []
        for marker in markers:
            title = '{} - {}'.format(marker['title'] or self.scene_title(marker['scene']), marker['primary_tag']['name'])
            item = self._create_item(marker['scene'], title=title, screenshot=marker['screenshot'])
            url = self._create_play_url(marker['scene']['id'])

            duration = marker['scene']['files'][0]['duration']
            item.setProperty('StartPercent', str(round(marker['seconds'] / duration * 100, 2)))
            item.addContextMenuItems(sort_menu)

            items.append((item, url))

        return count, items
