"""
A replacement root (/) handler that will send HAL
instead of the default when asked for HAL.

Unfortunately this will not work alongside other
plugins which _also_ replace the root handler. This
is, presumably, a bug.
"""

import tiddlyweb.web.handler

from tiddlyweb.web.util import get_serialize_type, server_base_url

from simplehal import HalDocument, Links, Link
from .serialization import Serialization

ROOT_LINKS = {
        'self': {'href': '/'},
        'alternate': {'href': '/', 'type': 'text/html'},
        'tiddlyweb:bags': {'href': '/bags'},
        'tiddlyweb:recipes': {'href': '/recipes'},
        'tiddlyweb:search': {'href': '/search{?q}', 'templated': True},
}

ORIGINAL_ROOT_HANDLER = tiddlyweb.web.handler.root


def replacement_root_handler(environ, start_response):
    """
    Check if we want HAL, if so send it, otherwise
    do the default.
    """
    _, mime_type = get_serialize_type(environ)
    if 'application/hal+json' in mime_type:
        return _hal_root(environ, start_response)
    else:
        return ORIGINAL_ROOT_HANDLER(environ, start_response)


def _hal_root(environ, start_response):
    """
    Compose a root HAL document linking to bags and recipes.
    """

    server_base = server_base_url(environ)
    links = Links()
    for rel in ROOT_LINKS:
        link = Link(rel, '%s%s' % (server_base, ROOT_LINKS[rel]['href']))
        kwargs = {}
        for key in ROOT_LINKS[rel]:
            if key is not 'href':
                kwargs[key] = ROOT_LINKS[rel][key]
        link.kwargs = kwargs
        links.add(link)
    links.add(Serialization.Curie)

    hal = HalDocument(links)

    start_response('200 OK', [('Content-Type',
        'application/hal+json; charset=UTF-8')])
    return [hal.to_json()]
