import requests
import urllib.parse


class StashInterface:
    def __init__(self, url, api_key):
        if not url.endswith('/graphql'):
            url = "{0}/graphql".format(url.rstrip("/"))

        self._headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "keep-alive",
            "ApiKey": api_key
        }
        self._url = url
        self._api_key = api_key

    def add_api_key(self, url: str):
        if self._api_key:
            url = "{}{}apikey={}".format(url, '&' if '?' in url else '?', urllib.parse.quote(self._api_key))

        return url

    def __call_graphql(self, query, variables=None):
        json = {'query': query}
        if variables is not None:
            json['variables'] = variables

        response = requests.post(self._url, json=json, headers=self._headers)

        if response.status_code == 200:
            result = response.json()
            if result.get("error", None):
                for error in result["error"]["errors"]:
                    raise Exception("GraphQL error: {}".format(error))
            if result.get("data", None):
                return result.get("data")
        else:
            raise Exception(
                "GraphQL query failed:{} - {}. Query: {}. Variables: {}".format(response.status_code, response.content,
                                                                                query, variables))

    def find_scenes(self, scene_filter=None, sort_field='title', sort_dir='asc'):
        query = """
query findScenes($scene_filter: SceneFilterType, $filter: FindFilterType!) {
  findScenes(scene_filter: $scene_filter, filter: $filter) {
    count
    scenes {
      id
      title
      details
      rating
      date
      created_at
      paths {
        screenshot
      }
      file {
        duration
        video_codec
        audio_codec
        width
        height
      }
      studio {
        name
      }
      performers {
        name
      }
      tags {
        name
      }
      scene_markers {
        id
      }
    }
  }
}
"""

        variables = {'filter': {
            'per_page': -1,
            'sort': sort_field,
            'direction': 'DESC' if sort_dir.lower() == 'desc' else 'ASC'
        }}

        if scene_filter is not None:
            variables['scene_filter'] = scene_filter

        result = self.__call_graphql(query, variables)

        return result["findScenes"]["count"], result["findScenes"]["scenes"]

    def find_scene(self, id):
        query = """
query findScene($id: ID) {
  findScene(id: $id) {
    id
    title
    details
    rating
    date
    created_at
    paths {
      stream
      screenshot
    }
    file {
      duration
      video_codec
      audio_codec
      width
      height
    }
    studio {
      name
    }
    performers {
      name
    }
    tags {
      name
    }
    scene_markers {
      id
      title
      seconds
      scene {
        id
        title
        details
        rating
        date
        created_at
        paths {
          screenshot
        }
        file {
          duration
          video_codec
          audio_codec
          width
          height
        }
        studio {
          name
        }
        performers {
          name
        }
        tags {
          name
        }
      }
      primary_tag {
        id
        name
      }
      tags {
        id
        name
      }
    }
  }
}
"""

        variables = {'id': id}

        return self.__call_graphql(query, variables)['findScene']

    def find_performers(self):
        query = """
query findPerformers($performer_filter: PerformerFilterType, $filter: FindFilterType!) {
  findPerformers(performer_filter: $performer_filter, filter: $filter) {
    count
    performers {
      id
      name
      details
      image_path
    }
  }
}
"""

        variables = {'filter': {
            'per_page': -1,
            'sort': 'name'
        },
            'performer_filter': {
                'scene_count': {
                    'modifier': 'GREATER_THAN',
                    'value': 0,
                }
            }
        }

        result = self.__call_graphql(query, variables)

        return result["findPerformers"]["count"], result["findPerformers"]["performers"]

    def find_tags(self):
        query = """
query findTags($tag_filter: TagFilterType, $filter: FindFilterType!) {
  findTags(tag_filter: $tag_filter, filter: $filter) {
    count
    tags {
      id
      name
      image_path
    }
  }
}
"""

        variables = {'filter': {
            'per_page': -1,
            'sort': 'name'
        },
            'tag_filter': {
                'scene_count': {
                    'modifier': 'GREATER_THAN',
                    'value': 0,
                }
            }
        }

        result = self.__call_graphql(query, variables)

        return result["findTags"]["count"], result["findTags"]["tags"]

    def find_studios(self):
        query = """
query findStudios($studio_filter: StudioFilterType, $filter: FindFilterType!) {
  findStudios(studio_filter: $studio_filter, filter: $filter) {
    count
    studios {
      id
      name
      image_path
      details
    }
  }
}
"""

        variables = {'filter': {
            'per_page': -1,
            'sort': 'name'
        },
            'studio_filter': {
                'scene_count': {
                    'modifier': 'GREATER_THAN',
                    'value': 0,
                }
            }
        }

        result = self.__call_graphql(query, variables)

        return result["findStudios"]["count"], result["findStudios"]["studios"]

    def find_scene_markers(self, markers_filter=None, sort_field='title', sort_dir=0):
        query = """
query findSceneMarkers($markers_filter: SceneMarkerFilterType, $filter: FindFilterType!) {
  findSceneMarkers(scene_marker_filter: $markers_filter, filter: $filter) {
    count
    scene_markers {
      id
      title
      seconds
      scene {
        id
        title
        details
        rating
        date
        created_at
        paths {
          screenshot
        }
        file {
          duration
          video_codec
          audio_codec
          width
          height
        }
        studio {
          name
        }
        performers {
          name
        }
        tags {
          name
        }
      }
      primary_tag {
        id
        name
      }
      tags {
        id
        name
      }
    }
  }
}
"""

        variables = {'filter': {
            'per_page': -1,
            'sort': sort_field,
            'direction': 'DESC' if sort_dir == 1 else 'ASC'
        }}

        if markers_filter is not None:
            variables['markers_filter'] = markers_filter

        result = self.__call_graphql(query, variables)

        return result["findSceneMarkers"]["count"], result["findSceneMarkers"]["scene_markers"]

    def find_saved_filters(self, mode):
        query = """
query findSavedFilters($mode: FilterMode!) {
    findSavedFilters(mode: $mode) {
        name
        filter
    }
}
"""

        variables = {'mode': mode}

        result = self.__call_graphql(query, variables)

        return result['findSavedFilters']

    def find_default_filter(self, mode):
        query = """
query findDefaultFilter($mode: FilterMode!) {
    findDefaultFilter(mode: $mode) {
        name
        filter
    }
}
"""

        variables = {'mode': mode}

        result = self.__call_graphql(query, variables)

        return result['findDefaultFilter']

    def scene_increment_o(self, id):
        query = """
mutation sceneIncrementO($id: ID!) {
  sceneIncrementO(id: $id)
}
"""

        variables = {'id': id}

        result = self.__call_graphql(query, variables)

        return result["sceneIncrementO"]
