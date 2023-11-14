import json


def parse(criterions):
    filter = {}

    for criterion in criterions:
        if criterion in ('sceneIsMissing', 'imageIsMissing', 'performerIsMissing', 'galleryIsMissing', 'tagIsMissing', 'studioIsMissing', 'studioIsMissing'):
            filter['is_missing'] = criterion['value']
        else:
            is_timestamp_field = criterion in ('created_at', 'updated_at', 'scene_created_at', 'scene_updated_at')
            value_transformer = (lambda v: v.replace(' ', 'T') if isinstance(v, str) else v) if is_timestamp_field else lambda v: v
            filter[criterion] = parse_criterion(criterions[criterion], value_transformer)

    return filter


def parse_criterion(criterion, value_transformer):
    filter = {}

    filter['modifier'] = criterion['modifier']

    value = criterion.get('value', '')
    if isinstance(value, dict) and 'depth' in value:
        if value.get('items') is not None:
            filter['value'] = list(map(lambda v: v['id'], value['items']))

        if value.get('excluded') is not None:
            filter['excludes'] = list(map(lambda v: v['id'], value['excluded']))

        filter['depth'] = value['depth']
    elif isinstance(value, dict) and not value.keys() - ['value', 'value2']:
        filter['value'] = value_transformer(value['value'])
        if 'value2' in value:
            filter['value2'] = value_transformer(value['value2'])
    elif isinstance(value, list):
        filter['value'] = list(map(lambda v: v['id'], value))
    elif isinstance(value, dict) and not value.keys() - ['endpoint', 'stashID']:
        filter['endpoint'] = value.get('endpoint')
        filter['stash_id'] = value.get('stashID')
    else:
        filter['value'] = value_transformer(value)

    return filter
