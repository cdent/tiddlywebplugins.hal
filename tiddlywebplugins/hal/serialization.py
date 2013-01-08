"""
A HAL Serialization for bags, recipes, tiddlers, composition only.
"""

from tiddlyweb.model.policy import Policy
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

    def bag_as(self, bag):
        """
        A single bag as HAL
        """
        bag_uri = bag_url(self.environ, bag, full=False)
        entity_structure = dict(policy=self._get_policy(bag.policy),
                desc=bag.desc, name=bag.name)
        return self._entity_as(entity_structure, bag_uri)

    def recipe_as(self, recipe):
        recipe_uri = recipe_url(self.environ, recipe, full=False)
        entity_structure = dict(policy=self._get_policy(recipe.policy),
                desc=recipe.desc, name=recipe.name, recipe=recipe.get_recipe())
        return self._entity_as(entity_structure, recipe_uri)

    def _entity_as(self, entity_structure, entity_uri):
        """
        A single bag or recipe.
        """
        links = Links()
        links.add(self.Curie)
        links.add(Link('tiddlyweb:tiddlers', entity_uri + '/tiddlers'))
        links.add(Link('self', entity_uri))
        hal_entity = HalDocument(links, data=entity_structure)
        return hal_entity.to_json()

    def _get_policy(self, policy):
        """
        Generate a dict of the policy.
        """
        return {key: getattr(policy, key) for key in Policy.attributes}

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
