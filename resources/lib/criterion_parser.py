import json


def parse(criterions):
    filter = {}

    for json_criterion in criterions:
        criterion = json.loads(json_criterion)

        type = criterion['type']
        if type in ('sceneIsMissing', 'imageIsMissing', 'performerIsMissing', 'galleryIsMissing', 'tagIsMissing', 'studioIsMissing', 'studioIsMissing'):
            filter['is_missing'] = criterion['value']
        else:
            filter[type] = parse_criterion(criterion)

    return filter


def parse_criterion(criterion):
    filter = {}

    filter['modifier'] = criterion['modifier']

    value = criterion.get('value', '')
    if isinstance(value, dict) and 'depth' in value:
        filter['value'] = list(map(lambda v: v['id'], value['items']))
        filter['depth'] = value['depth']
    elif isinstance(value, dict) and not value.keys() - ['value', 'value2']:
        filter.update(value)
    elif isinstance(value, list):
        filter['value'] = list(map(lambda v: v['id'], value))
    else:
        filter['value'] = value

    return filter
