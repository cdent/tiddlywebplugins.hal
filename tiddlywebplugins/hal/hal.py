"""
Classes encapsulating the structure of a HAL Document.
"""

import json

VALID_LINK_ATTRS = ['templated', 'type', 'name', 'profile', 'title',
    'hreflang']

class HalDocument(object):
    """
    A single HAL document, which can be nested in
    another.
    """

    def __init__(self, links, data=None, embed=None):
        if data:
            self.structure = data
        else:
            self.structure = {}
        if embed:
            self.structure['_embedded'] = embed
        self.structure['_links'] = links.structure

    def to_json(self):
        return json.dumps(self.structure)


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

    def __init__(self, rel, href, **kwargs):
        self.rel = rel
        self.href = href
        self.kwargs = kwargs

    def to_dict(self):
        result = {'href': self.href}
        for key in self.kwargs:
            if key in VALID_LINK_ATTRS:
                result[key] = self.kwargs[key]
        return result
