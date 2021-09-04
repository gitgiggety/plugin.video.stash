from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class StudioItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(self, client, 'studios', local.get_localized(30005), browse_for)

    def _create_items(self):
        (count, studios) = self._client.find_studios()
        items = []
        for studio in studios:
            criterion = {'studios': {'modifier': 'INCLUDES_ALL', 'value': [studio['id']], 'depth': 0}}
            item = self._create_item(studio['name'], studio['details'], studio['image_path'])
            url = self._create_url(studio['name'], criterion)
            items.append((item, url))

        return items
