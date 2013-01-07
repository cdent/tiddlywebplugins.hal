

def test_compile():
    try:
        import tiddlywebplugins.hal
        assert True
    except ImportError, exc:
        assert False, exc
