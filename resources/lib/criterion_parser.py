import json

resolution_map = {
    "144p": "VERY_LOW",
    "240p": "LOW",
    "360p": "R360P",
    "480p": "STANDARD",
    "540p": "WEB_HD",
    "720p": "STANDARD_HD",
    "1080p": "FULL_HD",
    "1440p": "QUAD_HD",
    "4k": "FOUR_K",
    "5k": "FIVE_K",
    "6k": "SIX_K",
    "7k": "SEVEN_K",
    "8k":   "EIGHT_K",
    "Huge": "HUGE",
}

def parse(criterions):
    filter = {}

    for name, criterion in criterions.items():
        if name in ('is_missing', 'has_markers'):
            filter[name] = criterion['value']
        elif name in ('organized', 'performer_favorite', 'interactive'):
            filter[name] = criterion['value'] == 'true'
        else:
            if name in ('resolution'):
                value_transformer = lambda v: resolution_map.get(v, '')
            elif name in ('created_at', 'updated_at', 'scene_created_at', 'scene_updated_at'):
                value_transformer = lambda v: v.replace(' ', 'T') if isinstance(v, str) else v
            else:
                value_transformer = lambda v: v

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
