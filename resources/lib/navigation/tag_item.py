from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class TagItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str, **kwargs):
        self._favorites = kwargs.get('favorites', False)
        type = kwargs['type'] if 'type' in kwargs else 'favorite_tags' if self._favorites else 'tags'
        label = kwargs['label'] if 'label' in kwargs else local.get_localized(30038 if self._favorites else 30004)
        NavigationItem.__init__(self, client, type, label, browse_for)

        self._filter_name = kwargs['filter_name'] if 'filter_name' in kwargs else 'tags' if self._favorites else type

    def _create_items(self, page=1, per_page=100):
        has_type = 'scenes' if self._type == 'scene_tags' else self._browse_for
        (count, tags) = self._client.find_tags(has_type=has_type, page=page, per_page=per_page,
                                               favorites=self._favorites)
        items = []
        for tag in tags:
            criterion = {self._filter_name: {'modifier': 'INCLUDES_ALL', 'value': [tag['id']]}}
            scenes = tag.get('scene_marker_count') if has_type == 'scene_markers' else tag.get('scene_count')
            item = self._create_item(tag['name'], tag.get('description'), tag['image_path'], scenes,
                                     tag.get('favorite', False))
            url = self._create_url(tag['name'], criterion)
            item.addContextMenuItems(self._favorite_menu('tag', tag['id'], tag.get('favorite', False)))
            items.append((item, url))

        return count, items
