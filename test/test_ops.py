"""
Test finding a particular bag and putting a tiddler there.
"""

import py.test

import shutil
import json

from pprint import pprint

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.web.serve import load_app

from tiddlywebplugins.utils import get_store

from simplehal import HalDocument, Resolver
from uritemplate import expand


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


def test_go_the_distance():
    # GET root
    response, content = http.request('http://0.0.0.0:8080/',
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200'
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'

    document = HalDocument.from_json(content)
    resolver = Resolver(document.get_curies())
    links = document.links

    assert 'tiddlyweb:bags' in links
    assert (resolver.expand('tiddlyweb:bags')
            == 'http://tiddlyweb.com/relations/bags')

    target_link = links['tiddlyweb:bags']['href']
    assert target_link == 'http://0.0.0.0:8080/bags'

    # GET bags
    response, content = http.request(target_link,
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200'
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'

    document = HalDocument.from_json(content)
    links = document.links

    data = document.get_data('tiddlyweb:bag')
    assert len(data) == 0

    bags_link = target_link

    # Make a bag
    assert 'tiddlyweb:bag' in links
    target_link = expand(links['tiddlyweb:bag']['href'], {'bag': 'mybag'})
    assert target_link == 'http://0.0.0.0:8080/bags/mybag'

    response, content = http.request(target_link,
            method='PUT',
            headers={'Content-Type': 'application/json'},
            body='{"desc": "my own special bag"}')

    assert response['status'] == '204'
    assert response['location'] == target_link

    # GET bags again, this time there is one
    response, content = http.request(bags_link,
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200'
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'

    document = HalDocument.from_json(content)
    links = document.links

    data = document.get_data('tiddlyweb:bag')
    assert len(data) == 1
    assert data[0]['name'] == 'mybag'

    # GET the single bag
    response, content = http.request(target_link,
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200'
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'
    document = HalDocument.from_json(content)
    links = document.links

    assert 'tiddlyweb:tiddlers' in links

    target_link = links['tiddlyweb:tiddlers']['href']

    # GET the (empty) tiddlers
    response, content = http.request(target_link,
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200', content
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'
    document = HalDocument.from_json(content)
    links = document.links

    data = document.get_data('tiddlyweb:tiddler')
    assert len(data) == 0

    tiddlers_link = target_link

    target_link = expand(links['tiddlyweb:tiddler']['href'],
            {'tiddler': 'mytiddler'})
    response, content = http.request(target_link,
            method='PUT',
            headers={'Content-Type': 'application/json'},
            body='{"text": "oh hai", "tags": ["tagone", "tagtwo"]}')

    assert response['status'] == '204'
    assert response['location'] == target_link

    # GET the (no longer empty) tiddlers
    response, content = http.request(tiddlers_link,
            headers={'Accept': 'application/hal+json'})
    assert response['status'] == '200', content
    assert response['content-type'] == 'application/hal+json; charset=UTF-8'
    document = HalDocument.from_json(content)
    links = document.links

    data = document.get_data('tiddlyweb:tiddler')
    assert len(data) == 1

    assert data[0]['title'] == 'mytiddler'
