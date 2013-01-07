"""
Description of My Plugin.
"""

import simplejson

import tiddlyweb.web.handler 

from tiddlyweb.web.util import get_serialize_type, bag_url
from tiddlyweb.serializations import SerializationInterface


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

class HalDocument(object):

    def __init__(self, links, data=None, embed=None):
        if data:
            self.structure = data
        else:
            self.structure = {}
        if embed:
            print 'embed', embed
            self.structure['_embedded'] = embed
        self.structure['_links'] = links.structure

    def to_json(self):
        return simplejson.dumps(self.structure)


class Links(object):
    """
    Model of a HAL links collection.
    """

    def __init__(self):
        self.structure = {}

    def add(self, link):
        if link.rel in self.structure:
            self.structure[link.rel] = [self.structure[link.rel]]
            self.structure[link.rel].append(link.to_dict())
        else:
            self.structure[link.rel] = link.to_dict()


class Link(object):
    """
    Model of a HAL link.
    """

    def __init__(self, rel, href, type=None):
        self.rel = rel
        self.href = href
        self.type = type

    def to_dict(self):
        result = {}
        for key in ['href', 'type']:
            value = getattr(self, key)
            if value:
                result[key] = value
        return result


class Serialization(SerializationInterface):

    def list_bags(self, bags):
        """
        Create a list of bags.
        """
        server_prefix = self.environ['tiddlyweb.config']['server_prefix']
        hal_bags = []
        for bag in bags:
           links = Links()
           links.add(Link('self', bag_url(self.environ, bag, full=False)))
           hal_bag = HalDocument(links, data={'name': bag.name})
           hal_bags.append(hal_bag.structure)
        links = Links()
        links.add(Link('self', '%s/%s' % (server_prefix, 'bags')))
        hal_doc = HalDocument(links, embed={'bag': hal_bags})
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
