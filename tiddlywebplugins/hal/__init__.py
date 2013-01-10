"""
Description of My Plugin.
"""

from tiddlywebplugins.utils import replace_handler

from .fixups import replacement_root_handler


EXTENSION_TYPES = {
        'hal': 'application/hal+json'
}
SERIALIZERS = {
        'application/hal+json': ['tiddlywebplugins.hal.serialization',
            'application/hal+json; charset=UTF-8']
}


def init(config):
    """
    Initialize the plugin by establishing the serialization.
    """
    config['extension_types'].update(EXTENSION_TYPES)
    config['serializers'].update(SERIALIZERS)
    if 'selector' in config:
        replace_handler(config['selector'], '/', dict(
            GET=replacement_root_handler))
