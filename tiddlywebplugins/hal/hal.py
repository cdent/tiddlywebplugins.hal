"""
Classes encapsulating the structure of a HAL Document.
"""

import json

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
            print 'embed', embed
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


