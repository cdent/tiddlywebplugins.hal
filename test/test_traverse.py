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
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.serve import load_app

from tiddlywebplugins.utils import get_store


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

    def app_fn():
        return load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    module.http = httplib2.Http()


def test_root():
    response, content = http.request('http://0.0.0.0:8080/')

    assert response['status'] == '200', content
    assert 'text/html' in response['content-type']

    response, content = http.request('http://0.0.0.0:8080/',
            headers={'Accept': 'application/hal+json'})

    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    assert info['_links']['self']['href'] == 'http://0.0.0.0:8080/'
    assert info['_links']['tiddlyweb:bags']['href'] == 'http://0.0.0.0:8080/bags'
    assert info['_links']['tiddlyweb:recipes']['href'] == 'http://0.0.0.0:8080/recipes'
    assert info['_links']['tiddlyweb:search']['href'] == 'http://0.0.0.0:8080/search{?q}'


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
    assert links['curie']['href'] == 'http://tiddlyweb.com/relations/{rel}'
    assert links['self']['href'] == 'http://0.0.0.0:8080/bags'

    bags = info['_embedded']['tiddlyweb:bag']
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

    # Handy for debugging, inspection etc.
    #print; pprint(info); print

    links = info['_links']
    assert links['curie']['href'] == 'http://tiddlyweb.com/relations/{rel}'
    assert links['self']['href'] == 'http://0.0.0.0:8080/recipes'

    recipes = info['_embedded']['tiddlyweb:recipe']
    assert len(recipes) == 5


def test_bag():
    bag = Bag('bag6')
    bag.policy.write = ['foobar']
    store.put(bag)

    response, content = http.request('http://0.0.0.0:8080/bags/bag6.hal')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    assert info['policy']['write'] == ['foobar']

    assert 'tiddlyweb:tiddlers' in links
    assert links['tiddlyweb:tiddlers']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers'
    assert links['tiddlyweb:bags']['href'] == 'http://0.0.0.0:8080/bags'


def test_recipe():
    recipe = Recipe('recipe6')
    recipe.policy.write = ['foobar']
    recipe.set_recipe([('bag5', ''), ('bag6', 'tag:monkey')])
    store.put(recipe)

    response, content = http.request('http://0.0.0.0:8080/recipes/recipe6.hal')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    assert info['policy']['write'] == ['foobar']
    assert len(info['recipe']) == 2
    assert info['recipe'][0][0] == 'bag5'
    assert info['recipe'][1][1] == 'tag:monkey'

    assert 'tiddlyweb:tiddlers' in links
    assert links['tiddlyweb:tiddlers']['href'] == 'http://0.0.0.0:8080/recipes/recipe6/tiddlers'
    assert links['tiddlyweb:recipes']['href'] == 'http://0.0.0.0:8080/recipes'


def test_bag_tiddlers():
    for i in range(5):
        tiddler = Tiddler('tiddler%s' % i, 'bag6')
        tiddler.text = 'text%s' % i
        tiddler.tags = ['tag%s' % i]
        store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0:8080/bags/bag6/tiddlers.hal')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    tiddlers = info['_embedded']['tiddlyweb:tiddler']

    assert len(tiddlers) == 5

    assert (tiddlers[0]['_links']['self']['href']
            == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler0')

    assert 'tiddlyweb:bag' in links
    assert links['tiddlyweb:bag']['href'] == 'http://0.0.0.0:8080/bags/bag6'


def test_bag_tiddler():
    response, content = http.request(
            'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4.hal')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']

    assert info['title'] == 'tiddler4'
    assert info['text'] == 'text4'
    assert info['tags'] == ['tag4']

    assert links['self']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4'
    assert links['tiddlyweb:tiddlers']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers'
    assert links['tiddlyweb:bag']['href'] == 'http://0.0.0.0:8080/bags/bag6'
    assert links['collection']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers'

def test_tiddler_revisions():
    tiddler = Tiddler('tiddler4', 'bag6')
    tiddler.text = 'new text'
    store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions.hal')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    tiddlers = info['_embedded']['tiddlyweb:revision']

    assert len(tiddlers) == 2

    assert (tiddlers[0]['_links']['self']['href']
            == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions/2')

    assert (links['self']['href']
            == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions')
    assert links['tiddlyweb:tiddler']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4'


def test_one_tiddler_revision():
    response, content = http.request(
            'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions/1.hal')

    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']

    assert (links['collection']['href']
            == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions')
    assert links['latest-version']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4'
    assert links['tiddlyweb:tiddler']['href'] == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4'
    assert (links['tiddlyweb:revisions']['href']
            == 'http://0.0.0.0:8080/bags/bag6/tiddlers/tiddler4/revisions')


def test_search():
    response, content = http.request(
            'http://0.0.0.0:8080/search.hal?q=text')
    assert response['status'] == '200', content
    assert 'application/hal+json' in response['content-type']
    info = json.loads(content)

    links = info['_links']
    assert 'curie' in links
