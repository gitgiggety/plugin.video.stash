from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class TagItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str, **kwargs):
        type = kwargs['type'] if 'type' in kwargs else 'tags'
        label = kwargs['label'] if 'label' in kwargs else local.get_localized(30004)
        NavigationItem.__init__(self, client, type, label, browse_for)

        self._filter_name = kwargs['filter_name'] if 'filter_name' in kwargs else type

    def _create_items(self):
        (count, tags) = self._client.find_tags(has_type='scenes' if self._type == 'scene_tags' else self._browse_for)
        items = []
        for tag in tags:
            criterion = {self._filter_name: {'modifier': 'INCLUDES_ALL', 'value': [tag['id']]}}
            item = self._create_item(tag['name'], image_path=tag['image_path'])
            url = self._create_url(tag['name'], criterion)
            items.append((item, url))

        return items
