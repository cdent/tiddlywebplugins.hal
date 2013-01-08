"""
Test traverse the entire api.
"""

import shutil
import json

from pprint import pprint

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.web.serve import load_app

from tiddlywebplugins.utils import get_store

MEANINGFUL_LINKS = ['bags', 'recipes', 'bag', 'recipe',
    'tiddlers', 'revisions']


def setup_module(module):
    """
    Set up a fresh new store and turn on the mock server.
    """
    try:
        shutil.rmtree('store')
    except:
        pass

    module.store = get_store(config)

    from tiddlywebplugins.hal import init
    init(config)

    def app_fn(): return load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    module.http = httplib2.Http()

    module.active_rels = []


def test_root():
    response, content = http.request('http://0.0.0.0:8080/')

    assert response['status'] == '200', content
    assert 'text/html' in response['content-type']

    response, content = http.request('http://0.0.0.0:8080/',
            headers={'Accept': 'application/hal+json'})

    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    assert info['_links']['self']['href'] == '/'
    assert info['_links']['bags']['href'] == '/bags'
    assert info['_links']['recipes']['href'] == '/recipes'


def test_bags():
    for i in range(5):
        bag = Bag('bag%s' % i)
        store.put(bag)

    response, content = http.request('http://0.0.0.0:8080/bags',
            headers={'Accept': 'application/hal+json'})

    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    assert links['self']['href'] == '/bags'

    bags = info['_embedded']['bag']
    assert len(bags) == 5


def test_recipes():
    for i in range(5):
        recipe = Recipe('recipe%s' % i)
        store.put(recipe)

    response, content = http.request('http://0.0.0.0:8080/recipes',
            headers={'Accept': 'application/hal+json'})

    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    assert links['self']['href'] == '/recipes'

    recipes = info['_embedded']['recipe']
    assert len(recipes) == 5
