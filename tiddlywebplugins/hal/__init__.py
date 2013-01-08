"""
Description of My Plugin.
"""

import tiddlyweb.web.handler 

from tiddlyweb.web.util import get_serialize_type, bag_url, recipe_url
from tiddlyweb.serializations import SerializationInterface

from .hal import HalDocument, Links, Link


ORIGINAL_ROOT_HANDLER = tiddlyweb.web.handler.root
EXTENSION_TYPES = {
        'hal': 'application/hal+json'
}
SERIALIZERS = {
        'application/hal+json': ['tiddlywebplugins.hal',
            'application/hal+json; charset=UTF-8']
}
ROOT_LINKS = {
        'self': { 'href': '/' },
        'alternate': { 'href': '/', 'type': 'text/html' },
        'bags': { 'href': '/bags' },
        'recipes': { 'href': '/recipes'}
}

class Serialization(SerializationInterface):

    def list_bags(self, bags):
        """
        Create a list of (embedded) bags.
        """
        return self._list_collection(bags, 'bags', 'bag', bag_url)

    def list_recipes(self, recipes):
        """
        Create a list of embedded recipes.
        """
        return self._list_collection(recipes, 'recipes', 'recipe', recipe_url)

    def _list_collection(self, entities, self_name, embed_name, url_maker):
        """
        Make a collection of either bags or recipes and retuns as
        HAL JSON.
        """
        server_prefix = self.environ['tiddlyweb.config']['server_prefix']
        hal_entities = []
        for entity in entities:
           links = Links()
           links.add(Link('self', url_maker(self.environ, entity, full=False)))
           hal_entity = HalDocument(links, data={'name': entity.name})
           hal_entities.append(hal_entity.structure)
        links = Links()
        links.add(Link('self', '%s/%s' % (server_prefix, self_name)))
        hal_doc = HalDocument(links, embed={embed_name: hal_entities})
        return hal_doc.to_json()


def replacement_root_handler(environ, start_response):
    """
    Check if we want HAL, if so send it, otherwise
    do the default.
    """
    serializer, mime_type = get_serialize_type(environ)
    if serializer == __name__:
        return _hal_root(environ, start_response)
    else:
        return ORIGINAL_ROOT_HANDLER(environ, start_response)


def _hal_root(environ, start_response):
    """
    Compose a root HAL document linking to bags and recipes.
    """

    server_prefix = environ['tiddlyweb.config']['server_prefix']
    links = Links()
    for rel in ROOT_LINKS:
        link = Link(rel, '%s%s' % (server_prefix, ROOT_LINKS[rel]['href']))
        if 'type' in ROOT_LINKS[rel]:
            link.type = ROOT_LINKS[rel]['type']
        links.add(link)

    hal = HalDocument(links)

    start_response('200 OK', [('Content-Type',
        'application/hal+json; charset=UTF-8')])
    return [hal.to_json()]


tiddlyweb.web.handler.root = replacement_root_handler


def init(config):
    config['extension_types'].update(EXTENSION_TYPES)
    config['serializers'].update(SERIALIZERS)
