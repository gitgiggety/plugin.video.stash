from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local


class StudioItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(self, client, 'studios', local.get_localized(30005), browse_for)

    def _create_items(self, page=1, per_page=100):
        (count, studios) = self._client.find_studios(page=page, per_page=per_page)
        items = []
        for studio in studios:
            criterion = {'studios': {'modifier': 'INCLUDES_ALL', 'value': [studio['id']], 'depth': 0}}
            item = self._create_item(studio['name'], studio['details'], studio['image_path'],
                                     studio.get('scene_count'), studio.get('favorite', False))
            url = self._create_url(studio['name'], criterion, sort_field='date', sort_dir='desc')
            item.addContextMenuItems(self._favorite_menu('studio', studio['id'], studio.get('favorite', False)))
            items.append((item, url))

        return count, items
