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

    if isinstance(criterion['value'], dict) and 'depth' in criterion['value']:
        filter['value'] = list(map(lambda v: v['id'], criterion['value']['items']))
        filter['depth'] = criterion['value']['depth']
    elif isinstance(criterion['value'], dict) and not criterion['value'].keys() - ['value', 'value2']:
        filter.update(criterion['value'])
    elif isinstance(criterion['value'], list):
        filter['value'] = list(map(lambda v: v['id'], criterion['value']))
    else:
        filter['value'] = criterion['value']

    return filter
