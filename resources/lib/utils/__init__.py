from urllib.parse import urlencode

BASE_URL = ''

def get_url(**kwargs):
    return '{}?{}'.format(BASE_URL, urlencode(kwargs))
