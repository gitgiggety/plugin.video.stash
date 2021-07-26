import json

def parse(criterions):
    filter = {}

    for json_criterion in criterions:
        criterion = json.loads(json_criterion)

        filter[criterion['type']] = parse_criterion(criterion)

    return filter

def parse_criterion(criterion):
    filter = {}

    filter['modifier'] = criterion['modifier']

    if isinstance(criterion['value'], list):
        filter['value'] = list(map(lambda v: v['id'], criterion['value']))
    else:
        filter['value'] = criterion['value']

    if 'depth' in criterion:
        filter['depth'] = criterion['depth']

    return filter
