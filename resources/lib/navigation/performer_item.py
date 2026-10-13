from .navigation_item import NavigationItem
from resources.lib.stash_interface import StashInterface
from resources.lib import utils
from resources.lib.utils import local


class PerformerItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str, favorites: bool = False):
        NavigationItem.__init__(self, client, 'favorite_performers' if favorites else 'performers',
                                local.get_localized(30021 if favorites else 30003), browse_for)
        self._favorites = favorites

    def _create_items(self, page=1, per_page=100):
        performer_filter = {'filter_favorites': True} if self._favorites else None
        (count, performers) = self._client.find_performers(performer_filter, page=page, per_page=per_page)
        items = []
        for performer in performers:
            name = performer['name']
            if performer.get('disambiguation'):
                name = '{} ({})'.format(name, performer['disambiguation'])
            criterion = {'performers': {'modifier': 'INCLUDES_ALL', 'value': [performer['id']]}}
            item = self._create_item(name, performer['details'], performer['image_path'],
                                     performer.get('scene_count'), performer.get('favorite', False))
            url = self._create_url(name, criterion, sort_field='date', sort_dir='desc')
            item.addContextMenuItems(
                [(local.get_localized(30054), 'RunPlugin({})'.format(utils.get_url(performer_info=performer['id'])))] +
                self._favorite_menu('performer', performer['id'], performer.get('favorite', False)))
            items.append((item, url))

        return count, items
