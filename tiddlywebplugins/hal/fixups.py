
import tiddlyweb.web.handler

from tiddlyweb.web.util import get_serialize_type

from .hal import HalDocument, Links, Link
from .serialization import Serialization

ROOT_LINKS = {
        'self': {'href': '/'},
        'alternate': {'href': '/', 'type': 'text/html'},
        'tiddlyweb:bags': {'href': '/bags'},
        'tiddlyweb:recipes': {'href': '/recipes'},
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

    server_prefix = environ['tiddlyweb.config']['server_prefix']
    links = Links()
    for rel in ROOT_LINKS:
        link = Link(rel, '%s%s' % (server_prefix, ROOT_LINKS[rel]['href']))
        if 'type' in ROOT_LINKS[rel]:
            link.kwargs['type'] = ROOT_LINKS[rel]['type']
        links.add(link)
    links.add(Serialization.Curie)

    hal = HalDocument(links)

    start_response('200 OK', [('Content-Type',
        'application/hal+json; charset=UTF-8')])
    return [hal.to_json()]
