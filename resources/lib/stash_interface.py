import requests

class StashInterface:
    url = ""
    headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "keep-alive",
            }

    def __init__(self, url, api_key):
        if not url.endswith('/graphql'):
            url = "{0}/graphql".format(url.rstrip("/"))

        self.headers['ApiKey'] = api_key
        self.url = url

    def __callGraphQL(self, query, variables = None):
        json = {}
        json['query'] = query
        if variables != None:
            json['variables'] = variables

        response = requests.post(self.url, json=json, headers=self.headers)

        if response.status_code == 200:
            result = response.json()
            if result.get("error", None):
                for error in result["error"]["errors"]:
                    raise Exception("GraphQL error: {}".format(error))
            if result.get("data", None):
                return result.get("data")
        else:
            raise Exception("GraphQL query failed:{} - {}. Query: {}. Variables: {}".format(response.status_code, response.content, query, variables))

    def findScenes(self, scene_filter = None, sort_field = 'title', sort_dir = 0):
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
            'direction': 'DESC' if sort_dir == 1 else 'ASC'
        }}

        if scene_filter != None:
            variables['scene_filter'] = scene_filter

        result = self.__callGraphQL(query, variables)

        return (result["findScenes"]["count"], result["findScenes"]["scenes"])

    def findScene(self, id):
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

        return self.__callGraphQL(query, variables)['findScene']

    def findPerformers(self):
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

        result = self.__callGraphQL(query, variables)

        return (result["findPerformers"]["count"], result["findPerformers"]["performers"])

    def findTags(self):
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

        result = self.__callGraphQL(query, variables)

        return (result["findTags"]["count"], result["findTags"]["tags"])

    def findStudios(self):
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

        result = self.__callGraphQL(query, variables)

        return (result["findStudios"]["count"], result["findStudios"]["studios"])

    def findSceneMarkers(self, markers_filter = None, sort_field = 'title', sort_dir = 0):
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

        if markers_filter != None:
            variables['markers_filter'] = markers_filter

        result = self.__callGraphQL(query, variables)

        return (result["findSceneMarkers"]["count"], result["findSceneMarkers"]["scene_markers"])

    def findSavedFilters(self, mode):
        query = """
query findSavedFilters($mode: FilterMode!) {
    findSavedFilters(mode: $mode) {
        name
        filter
    }
}
"""

        variables = {'mode': mode}

        result = self.__callGraphQL(query, variables)

        return result['findSavedFilters']

    def findDefaultFilter(self, mode):
        query = """
query findDefaultFilter($mode: FilterMode!) {
    findDefaultFilter(mode: $mode) {
        name
        filter
    }
}
"""

        variables = {'mode': mode}

        result = self.__callGraphQL(query, variables)

        return result['findDefaultFilter']

    def sceneIncrementO(self, id):
        query = """
mutation sceneIncrementO($id: ID!) {
  sceneIncrementO(id: $id)
}
"""

        variables = {'id': id}

        result = self.__callGraphQL(query, variables)

        return (result["sceneIncrementO"])
