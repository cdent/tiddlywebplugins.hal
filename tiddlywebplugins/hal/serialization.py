"""
A HAL Serialization for bags, recipes, tiddlers, composition only.
"""

from base64 import b64encode

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.serializations.json import Serialization as JSON
from tiddlyweb.web.util import bag_url, recipe_url, tiddler_url, encode_name
from tiddlyweb.util import binary_tiddler

from .hal import HalDocument, Links, Link


class Serialization(JSON):
    """
    An implementation of SerializationInterface for presenting
    HAL. Subclasses the JSON serialization which provides two
    things:

    _tiddler_dict for representing the guts of a tiddler
    the as_* methods, for handling writes
    """

    # To, eventually, have some discoverability.
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

    def list_tiddlers(self, tiddlers):
        """
        Create a list of embedded tiddlers. What link rels are needed
        is dependent on context, which we have to...guess.
        """

        hal_entities, embed_name, info_tiddler = self._embedded_tiddlers(
                tiddlers)

        links = Links()
        tiddler_links = self._tiddlers_links(tiddlers, info_tiddler)
        for rel in tiddler_links:
            links.add(Link(rel, tiddler_links[rel]))
        links.add(self.Curie)

        hal_doc = HalDocument(links, embed={embed_name: hal_entities})
        return hal_doc.to_json()

    def bag_as(self, bag):
        """
        A single bag as HAL
        """
        bag_uri = bag_url(self.environ, bag, full=False)
        entity_structure = dict(policy=self._get_policy(bag.policy),
                desc=bag.desc, name=bag.name)
        return self._entity_as(entity_structure, bag_uri, 'bags')

    def recipe_as(self, recipe):
        recipe_uri = recipe_url(self.environ, recipe, full=False)
        entity_structure = dict(policy=self._get_policy(recipe.policy),
                desc=recipe.desc, name=recipe.name, recipe=recipe.get_recipe())
        return self._entity_as(entity_structure, recipe_uri, 'recipes')

    def tiddler_as(self, tiddler):
        links = Links()
        links.add(self.Curie)

        if 'revision' in self.environ['wsgiorg.routing_args'][1]:
            for link in self._revision_links(tiddler):
                links.add(link)
        else:
            for link in self._tiddler_links(tiddler):
                links.add(link)

        hal_entity = HalDocument(links, data=self._tiddler_dict(
            tiddler, fat=True))
        return hal_entity.to_json()

    def _embedded_entities(self, entities, url_maker):
        """
        Calculate the entities embedded in bags or recipes.
        """
        def make_document(entity):
            links = Links()
            links.add(Link('self',
                url_maker(self.environ, entity, full=False)))
            return HalDocument(links, data={'name': entity.name}).structure

        return [make_document(entity) for entity in entities]

    def _embedded_tiddlers(self, tiddlers):
        """
        Calculate the embedded tiddlers, return them, a
        embed rel and if appropriate a single tiddler
        holding bag and/or recipe information.
        """
        hal_entities = []
        tiddler = None
        embed_name = 'tiddlyweb:tiddler'
        for tiddler in tiddlers:
            links = Links()
            tiddler_link = tiddler_url(self.environ, tiddler, full=False)
            if tiddlers.is_revisions:
                tiddler_link += '/revisions/%s' % encode_name(
                        unicode(tiddler.revision))
                embed_name = 'tiddlyweb:revision'
            links.add(Link('self', tiddler_link))
            hal_entity = HalDocument(links,
                    data=self._tiddler_dict(tiddler))
            hal_entities.append(hal_entity.structure)
        return (hal_entities, embed_name, tiddler)

    def _entity_as(self, entity_structure, entity_uri, container):
        """
        A single bag or recipe.
        """
        server_prefix = self.environ['tiddlyweb.config']['server_prefix']
        links = Links()
        links.add(self.Curie)
        links.add(Link('tiddlyweb:%s' % container,
            '%s/%s' % (server_prefix, container)))
        links.add(Link('tiddlyweb:tiddlers', entity_uri + '/tiddlers'))
        links.add(Link('self', entity_uri))
        hal_entity = HalDocument(links, data=entity_structure)
        return hal_entity.to_json()

    def _get_policy(self, policy):
        """
        Generate a dict of the policy.
        """
        #return {key: getattr(policy, key) for key in Policy.attributes}
        return dict([(key, getattr(policy, key)) for key in Policy.attributes])

    def _list_collection(self, entities, self_name, embed_name, url_maker):
        """
        Make a collection of either bags or recipes and retuns as
        HAL JSON.
        """
        server_prefix = self.environ['tiddlyweb.config']['server_prefix']
        hal_entities = self._embedded_entities(entities, url_maker)
        links = Links()
        links.add(Link('self', '%s/%s' % (server_prefix, self_name)))
        links.add(self.Curie)
        hal_doc = HalDocument(links, embed={
            'tiddlyweb:%s' % embed_name: hal_entities})
        return hal_doc.to_json()

    def _revision_links(self, tiddler):
        """
        The links to provide with a single revision.
        """
        tiddler_link = tiddler_url(self.environ, tiddler, full=False)
        return [
            Link('latest-version', tiddler_link),
            Link('tiddlyweb:tiddler', tiddler_link),
            Link('collection', tiddler_link + '/revisions'),
            Link('tiddlyweb:revisions', tiddler_link + '/revisions')
        ]

    def _tiddler_links(self, tiddler):
        """
        The links to provie with a single tiddler.
        """
        links = []
        tiddler_link = tiddler_url(self.environ, tiddler, full=False)
        collection_link = self._tiddlers_links(Tiddlers(), tiddler)['self']
        links.append(Link('tiddlyweb:tiddlers', collection_link))
        links.append(Link('collection', collection_link))
        links.append(Link('tiddlyweb:bag', bag_url(self.environ,
            Bag(tiddler.bag), full=False)))
        if tiddler.recipe:
            links.append(Link('tiddlyweb:recipe', recipe_url(self.environ,
                Recipe(tiddler.recipe), full=False)))
        links.append(Link('self', tiddler_link))
        return links

    def _tiddlers_links(self, tiddlers, tiddler):
        """
        Establish the links to use with a tiddlers collection.
        If the collection is a search or revisions we need to
        do some special work, otherwise just look at the last
        tiddler in the collection to determine the container.
        """
        if tiddlers.is_search:
            return {}

        if tiddlers.is_revisions:
            links = {}
            links['self'] = '%s/%s/revisions' % (
                    self._tiddlers_self(tiddler)['self'],
                    encode_name(tiddler.title))
            links['tiddlyweb:tiddler'] = tiddler_url(self.environ,
                    tiddler, full=False)
            return links

        if tiddler:
            return self._tiddlers_self(tiddler)

    def _tiddlers_self(self, tiddler):
        """
        Given a single tiddler from a collection determine the
        self URI of that collection.
        """
        links = {}
        if tiddler.recipe:
            tiddlers_container = recipe_url(self.environ,
                    Recipe(tiddler.recipe), full=False)
            links['tiddlyweb:recipe'] = tiddlers_container
        else:
            tiddlers_container = bag_url(self.environ, Bag(tiddler.bag),
                    full=False)
            links['tiddlyweb:bag'] = tiddlers_container
        links['self'] = tiddlers_container + '/tiddlers'
        return links
