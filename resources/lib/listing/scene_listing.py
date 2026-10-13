import json
from typing import Optional
import xbmcgui

from .listing import Listing
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local, get_url, autoplay
from resources.lib.navigation import NavigationItem, StudioItem, TagItem, PerformerItem


class SceneListing(Listing):
    def __init__(self, client: StashInterface):
        Listing.__init__(self, client, 'scenes', local.get_localized(30006), filter_type='SCENES')

    def get_navigation(self) -> [NavigationItem]:
        return [
            PerformerItem(self._client, 'scenes'),
            TagItem(self._client, 'scenes'),
            StudioItem(self._client, 'scenes'),
        ]

    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        browse = params['browse']
        if browse == 'performers':
            return PerformerItem(self._client, 'scenes')
        if browse == 'favorite_performers':
            return PerformerItem(self._client, 'scenes', favorites=True)
        if browse == 'tags':
            return TagItem(self._client, 'scenes')
        if browse == 'favorite_tags':
            return TagItem(self._client, 'scenes', favorites=True)
        if browse == 'studios':
            return StudioItem(self._client, 'scenes')

    def sort_options(self):
        return [
            (local.get_localized(30025), 'title', 'asc'),
            (local.get_localized(30026), 'created_at', 'desc'),
            (local.get_localized(30027), 'date', 'desc'),
            (local.get_localized(30020), 'random', 'asc'),
            (local.get_localized(30028), 'rating', 'desc'),
            (local.get_localized(30029), 'play_count', 'desc'),
            (local.get_localized(30030), 'last_played_at', 'desc'),
            (local.get_localized(30031), 'duration', 'desc'),
            (local.get_localized(30032), 'o_counter', 'desc'),
        ]

    def _create_items(self, criterion: dict, sort_field: str, sort_dir: str, params: dict, page=1, per_page=40):
        (count, scenes) = self._client.find_scenes(criterion, sort_field, sort_dir, page=page, per_page=per_page,
                                                   q=params.get('q'))
        sort_menu = self._context_menu(params)
        play_next = autoplay()
        items = []
        for scene in scenes:
            item = self._create_item(scene)
            if play_next:
                # Not playable itself: play_from builds a playlist starting at this scene
                url = get_url(**dict(params, play_from=scene['id']))
                item.setProperty('IsPlayable', 'false')
            else:
                url = self._create_play_url(scene['id'])

            menu = []
            if len(scene['scene_markers']) > 0:
                menu.append((local.get_localized(30010),
                             'ActivateWindow(videos, {})'.format(get_url(list='scene_markers', scene=scene['id']))))
            menu.append(
                (local.get_localized(30008), 'RunPlugin({})'.format(get_url(increment_o='', scene=scene['id']))))
            menu.append((local.get_localized(30041), 'RunPlugin({})'.format(get_url(rate_scene=scene['id'], rating=scene.get('rating100') or 0))))
            if scene['performers']:
                menu.append((local.get_localized(30042),
                             'RunPlugin({})'.format(get_url(scene_performers=scene['id']))))
            item.addContextMenuItems(menu + sort_menu)

            items.append((item, url))

        return count, items

    def queue(self, params: dict, scene_id: str, per_page: int) -> [dict]:
        """The scene and the ones after it in the listing it was started from (this page and the next)"""
        criterion = json.loads(params['criterion']) if 'criterion' in params else {}
        page = int(params.get('page', 1))
        args = dict(sort_field=params.get('sort_field'), sort_dir=params.get('sort_dir', 'asc'), per_page=per_page,
                    q=params.get('q'))
        (count, scenes) = self._client.find_scenes(criterion, page=page, **args)
        if page * per_page < count:
            scenes = scenes + self._client.find_scenes(criterion, page=page + 1, **args)[1]
        ids = [scene['id'] for scene in scenes]
        return scenes[ids.index(scene_id):] if scene_id in ids else [self._client.find_scene(scene_id)]
