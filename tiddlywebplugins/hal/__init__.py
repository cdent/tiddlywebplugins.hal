"""
Description of My Plugin.
"""

import tiddlyweb.web.handler

from tiddlyweb.web.util import get_serialize_type

from .hal import HalDocument, Links, Link


ORIGINAL_ROOT_HANDLER = tiddlyweb.web.handler.root
EXTENSION_TYPES = {
        'hal': 'application/hal+json'
}
SERIALIZERS = {
        'application/hal+json': ['tiddlywebplugins.hal.serialization',
            'application/hal+json; charset=UTF-8']
}
ROOT_LINKS = {
        'self': {'href': '/'},
        'alternate': {'href': '/', 'type': 'text/html'},
        'bags': {'href': '/bags'},
        'recipes': {'href': '/recipes'}
}


def replacement_root_handler(environ, start_response):
    """
    Check if we want HAL, if so send it, otherwise
    do the default.
    """
    serializer, mime_type = get_serialize_type(environ)
    if 'application/hal+json' in mime_type:
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
