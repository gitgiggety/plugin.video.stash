import gzip
import json
import urllib.error
import urllib.parse
import urllib.request

SCENE_FIELDS = """
      id
      title
      details
      rating100
      date
      created_at
      play_count
      resume_time
      last_played_at
      o_counter
      paths {
        screenshot
      }
      files {
        basename
        duration
        video_codec
        audio_codec
        width
        height
      }
      studio {
        name
        image_path
      }
      performers {
        id
        name
        image_path
        favorite
      }
      tags {
        name
      }
"""

MARKER_FIELDS = """
      id
      title
      seconds
      screenshot
      scene {
""" + SCENE_FIELDS + """
      }
      primary_tag {
        id
        name
      }
      tags {
        id
        name
      }
"""


class StashInterface:
    def __init__(self, url, api_key):
        if not url.endswith('/graphql'):
            url = "{0}/graphql".format(url.rstrip("/"))

        self._headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "ApiKey": api_key
        }
        self._url = url
        self._api_key = api_key

    def add_api_key(self, url: str):
        if url and self._api_key:
            url = "{}{}apikey={}".format(url, '&' if '?' in url else '?', urllib.parse.quote(self._api_key))

        return url

    def __call_graphql(self, query, variables=None):
        body = {'query': query}
        if variables is not None:
            body['variables'] = variables

        # urllib instead of requests: importing requests takes over a second on low-end devices
        request = urllib.request.Request(self._url, data=json.dumps(body).encode('utf-8'), headers=self._headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
                if response.headers.get('Content-Encoding') == 'gzip':
                    content = gzip.decompress(content)
        except urllib.error.HTTPError as e:
            raise Exception(
                "GraphQL query failed:{} - {}. Query: {}. Variables: {}".format(e.code, e.read(), query, variables))

        result = json.loads(content.decode('utf-8'))
        if result.get("errors", None):
            for error in result["errors"]:
                raise Exception("GraphQL error: {}".format(error['message']))
        if result.get("data", None):
            return result.get("data")

    @staticmethod
    def _find_filter(sort_field, sort_dir, page, per_page, q=None):
        find_filter = {
            'page': page,
            'per_page': per_page,
            'sort': sort_field,
            'direction': 'DESC' if str(sort_dir).lower() in ('desc', '1') else 'ASC'
        }
        if q:
            find_filter['q'] = q

        return find_filter

    def find_scenes(self, scene_filter=None, sort_field='title', sort_dir='asc', page=1, per_page=40, q=None):
        query = """
query findScenes($scene_filter: SceneFilterType, $filter: FindFilterType!) {
  findScenes(scene_filter: $scene_filter, filter: $filter) {
    count
    scenes {
""" + SCENE_FIELDS + """
      scene_markers {
        id
      }
    }
  }
}
"""

        variables = {'filter': self._find_filter(sort_field or 'title', sort_dir, page, per_page, q)}

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
    rating100
    date
    created_at
    sceneStreams {
      url
      mime_type
      label
      __typename
    }
    paths {
      stream
      screenshot
    }
    files {
      basename
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
""" + MARKER_FIELDS + """
    }
  }
}
"""

        variables = {'id': id}

        return self.__call_graphql(query, variables)['findScene']

    def find_performers(self, performer_filter=None, sort_field='name', sort_dir='asc', page=1, per_page=100, q=None):
        query = """
query findPerformers($performer_filter: PerformerFilterType, $filter: FindFilterType!) {
  findPerformers(performer_filter: $performer_filter, filter: $filter) {
    count
    performers {
      id
      name
      disambiguation
      details
      image_path
      favorite
      scene_count
    }
  }
}
"""

        performer_filter = dict(performer_filter or {})
        performer_filter.setdefault('scene_count', {'modifier': 'GREATER_THAN', 'value': 0})
        variables = {'filter': self._find_filter(sort_field, sort_dir, page, per_page, q),
                     'performer_filter': performer_filter}

        result = self.__call_graphql(query, variables)

        return result["findPerformers"]["count"], result["findPerformers"]["performers"]

    def find_tags(self, has_type=None, sort_field='name', sort_dir='asc', page=1, per_page=100, q=None,
                  favorites=False):
        query = """
query findTags($tag_filter: TagFilterType, $filter: FindFilterType!) {
  findTags(tag_filter: $tag_filter, filter: $filter) {
    count
    tags {
      id
      name
      description
      image_path
      favorite
      scene_count
      scene_marker_count
    }
  }
}
"""

        tag_filter = {}
        if has_type is not None:
            count_type = 'marker_count' if has_type == 'scene_markers' else 'scene_count'
            tag_filter[count_type] = {'modifier': 'GREATER_THAN', 'value': 0}
        if favorites:
            tag_filter['favorite'] = True

        variables = {'filter': self._find_filter(sort_field, sort_dir, page, per_page, q),
                     'tag_filter': tag_filter}

        result = self.__call_graphql(query, variables)

        return result["findTags"]["count"], result["findTags"]["tags"]

    def find_studios(self, sort_field='name', sort_dir='asc', page=1, per_page=100, q=None):
        query = """
query findStudios($studio_filter: StudioFilterType, $filter: FindFilterType!) {
  findStudios(studio_filter: $studio_filter, filter: $filter) {
    count
    studios {
      id
      name
      image_path
      details
      favorite
      scene_count
    }
  }
}
"""

        variables = {'filter': self._find_filter(sort_field, sort_dir, page, per_page, q),
                     'studio_filter': {'scene_count': {'modifier': 'GREATER_THAN', 'value': 0}}}

        result = self.__call_graphql(query, variables)

        return result["findStudios"]["count"], result["findStudios"]["studios"]

    def find_scene_markers(self, markers_filter=None, sort_field='title', sort_dir='asc', page=1, per_page=40, q=None):
        query = """
query findSceneMarkers($markers_filter: SceneMarkerFilterType, $filter: FindFilterType!) {
  findSceneMarkers(scene_marker_filter: $markers_filter, filter: $filter) {
    count
    scene_markers {
""" + MARKER_FIELDS + """
    }
  }
}
"""

        variables = {'filter': self._find_filter(sort_field or 'title', sort_dir, page, per_page, q)}

        if markers_filter is not None:
            variables['markers_filter'] = markers_filter

        result = self.__call_graphql(query, variables)

        return result["findSceneMarkers"]["count"], result["findSceneMarkers"]["scene_markers"]

    def find_saved_filters(self, mode):
        query = """
query findSavedFilters($mode: FilterMode!) {
    findSavedFilters(mode: $mode) {
        name,
        object_filter,
        find_filter {
          q
          page
          per_page
          sort
          direction
      }
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
        name,
        object_filter,
        find_filter {
          q
          page
          per_page
          sort
          direction
      }
    }
}
"""

        variables = {'mode': mode}

        result = self.__call_graphql(query, variables)

        return result['findDefaultFilter']

    def scene_add_o(self, id):
        # sceneIncrementO was removed from Stash, sceneAddO replaces it
        try:
            result = self.__call_graphql("""
mutation sceneAddO($id: ID!) {
  sceneAddO(id: $id) {
    count
  }
}
""", {'id': id})
            return result["sceneAddO"]["count"]
        except Exception:
            result = self.__call_graphql("""
mutation sceneIncrementO($id: ID!) {
  sceneIncrementO(id: $id)
}
""", {'id': id})
            return result["sceneIncrementO"]

    def scene_add_play(self, id):
        result = self.__call_graphql("""
mutation sceneAddPlay($id: ID!) {
  sceneAddPlay(id: $id) {
    count
  }
}
""", {'id': id})
        return result["sceneAddPlay"]["count"]

    def scene_save_activity(self, id, resume_time: float, play_duration: float):
        self.__call_graphql("""
mutation sceneSaveActivity($id: ID!, $resume_time: Float, $playDuration: Float) {
  sceneSaveActivity(id: $id, resume_time: $resume_time, playDuration: $playDuration)
}
""", {'id': id, 'resume_time': resume_time, 'playDuration': play_duration})

    def ui_configuration(self) -> dict:
        return self.__call_graphql("{ configuration { ui } }")["configuration"]["ui"] or {}

    def set_favorite(self, kind: str, id, favorite: bool) -> bool:
        """kind: performer, tag or studio"""
        mutation = """
mutation {0}Update($input: {1}UpdateInput!) {{
  {0}Update(input: $input) {{
    favorite
  }}
}}
""".format(kind, kind.capitalize())
        result = self.__call_graphql(mutation, {'input': {'id': id, 'favorite': favorite}})
        return result[kind + 'Update']['favorite']

    def set_scene_rating(self, id, rating100):
        self.__call_graphql("""
mutation sceneUpdate($input: SceneUpdateInput!) {
  sceneUpdate(input: $input) {
    id
  }
}
""", {'input': {'id': id, 'rating100': rating100}})

    def find_performer(self, id):
        return self.__call_graphql("""
query findPerformer($id: ID!) {
  findPerformer(id: $id) {
    id
    name
    disambiguation
    alias_list
    birthdate
    death_date
    country
    ethnicity
    hair_color
    eye_color
    height_cm
    measurements
    career_length
    tattoos
    piercings
    details
    favorite
    rating100
    scene_count
    image_path
    tags {
      name
    }
  }
}
""", {'id': id})['findPerformer']
