import json


def parse(criterions):
    filter = {}

    for name, criterion in criterions.items():
        if name in ('is_missing', 'has_markers'):
            filter[name] = criterion['value']
        elif name in ('organized', 'performer_favorite', 'interactive'):
            filter[name] = criterion['value'] == 'true'
        else:
            is_timestamp_field = name in ('created_at', 'updated_at', 'scene_created_at', 'scene_updated_at')
            value_transformer = (lambda v: v.replace(' ', 'T') if isinstance(v, str) else v) if is_timestamp_field else lambda v: v
            filter[name] = parse_criterion(criterion, value_transformer)

    return filter


def parse_criterion(criterion, value_transformer):
    filter = {}

    filter['modifier'] = criterion['modifier']

    value = criterion.get('value', '')
    if isinstance(value, dict) and not value.keys() - ['items', 'excluded', 'depth']:
        if value.get('items') is not None:
            filter['value'] = list(map(lambda v: v['id'], value['items']))

        if value.get('excluded') is not None:
            filter['excludes'] = list(map(lambda v: v['id'], value['excluded']))

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
