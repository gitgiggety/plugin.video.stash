import json
from resources.lib.utils.resolutions import Resolution_map

""" elif "resolution" == criterion:
            val = criterion["resolution"]["modifier"]["value"]
            criterion["resolution"]["modifier"]["value"] = Resolution_map[val] """


def parse(criterions):
    filter = {}

    for criterion in criterions:
        if criterion in ('sceneIsMissing', 'imageIsMissing', 'performerIsMissing', 'galleryIsMissing', 'tagIsMissing', 'studioIsMissing', 'studioIsMissing'):
            filter['is_missing'] = criterion['value']
        else:
            if "resolution" == criterion:
                val = criterions[criterion]["value"]
                criterions[criterion]["value"] = Resolution_map[val]
            is_timestamp_field = criterion in (
                'created_at', 'updated_at', 'scene_created_at', 'scene_updated_at')
            value_transformer = (lambda v: v.replace(' ', 'T') if isinstance(
                v, str) else v) if is_timestamp_field else lambda v: v
            filter[criterion] = parse_criterion(
                criterions[criterion], value_transformer)

    return filter


def parse_criterion(criterion, value_transformer):
    filter = {}

    filter['modifier'] = criterion['modifier']

    value = criterion.get('value', '')

    if isinstance(value, dict) and not value.keys() - ['items', 'excluded', 'depth']:
        if value.get('items') is not None:
            filter['value'] = list(map(lambda v: v['id'], value['items']))

        if value.get('excluded') is not None:
            filter['excludes'] = list(
                map(lambda v: v['id'], value['excluded']))

        if value.get('depth') is not None:
            filter['depth'] = value['depth']
    elif isinstance(value, dict) and not value.keys() - ['value', 'value2']:
        filter['value'] = value_transformer(value['value'])
        if 'value2' in value:
            filter['value2'] = value_transformer(value['value2'])
    elif isinstance(value, dict) and not value.keys() - ['endpoint', 'stashID']:
        filter['endpoint'] = value.get('endpoint')
        filter['stash_id'] = value.get('stashID')
    else:
        filter['value'] = value_transformer(value)

    return filter
