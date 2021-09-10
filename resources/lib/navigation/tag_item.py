from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class TagItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(self, client, 'tags', local.get_localized(30004), browse_for)

    def _create_items(self):
        (count, tags) = self._client.find_tags()
        items = []
        for tag in tags:
            criterion = {'tags': {'modifier': 'INCLUDES_ALL', 'value': [tag['id']], 'depth': 0}}
            item = self._create_item(tag['name'], image_path=tag['image_path'])
            url = self._create_url(tag['name'], criterion)
            items.append((item, url))

        return items
