from .listing import Listing
from .scene_listing import SceneListing
from .scene_marker_listing import SceneMarkerListing
from resources.lib.stash_interface import StashInterface


def create_listing(type: str, client: StashInterface) -> Listing:
    if type == 'scenes':
        return SceneListing(client)
    elif type == 'scene_markers':
        return SceneMarkerListing(client)
