import json


def parse(criterions):
    filter = {}

    for criterion in criterions:
        if criterion in ('sceneIsMissing', 'imageIsMissing', 'performerIsMissing', 'galleryIsMissing', 'tagIsMissing', 'studioIsMissing', 'studioIsMissing'):
            filter['is_missing'] = criterion['value']
        else:
            filter[criterion] = parse_criterion(criterions[criterion])

    return filter


def parse_criterion(criterion):
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
        filter.update(value)
    elif isinstance(value, list):
        filter['value'] = list(map(lambda v: v['id'], value))
    elif 'value' in criterion:
        filter['value'] = value

    return filter
