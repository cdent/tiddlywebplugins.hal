"""
A HAL Serialization for bags, recipes, tiddlers, composition only.
"""

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import bag_url, recipe_url

from .hal import HalDocument, Links, Link


class Serialization(SerializationInterface):
    """
    An implementation of SerializationInterface for presenting
    HAL.
    """
    
    Curie = Link('curie', 'http://tiddlyweb.com/relations/{rel}',
            templated=True, name='tiddlyweb')

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
        links.add(self.Curie)
        hal_doc = HalDocument(links, embed={embed_name: hal_entities})
        return hal_doc.to_json()
