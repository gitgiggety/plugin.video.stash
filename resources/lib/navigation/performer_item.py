from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class PerformerItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(self, client, 'performers', local.get_localized(30003), browse_for)

    def _create_items(self):
        (count, performers) = self._client.find_performers()
        items = []
        for performer in performers:
            criterion = {'performers': {'modifier': 'INCLUDES_ALL', 'value': [performer['id']]}}
            item = self._create_item(performer['name'], performer['details'], performer['image_path'])
            url = self._create_url(performer['name'], criterion)
            items.append((item, url))

        return items
