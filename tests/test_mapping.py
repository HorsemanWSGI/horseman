import pytest
from horseman.meta import Node
from horseman.mapping import Mapping
from horseman.response import Response


def basic_app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


def other_app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    return [b"Something else\n"]


def test_mapping():
    node = Mapping()
    assert isinstance(node, Node)


def test_normalizing():
    with pytest.raises(ValueError):
        assert Mapping.normalize(1)
    assert Mapping.normalize('/test') == '/test'
    assert Mapping.normalize("/") == '/'
    assert Mapping.normalize("////") == '/'
    assert Mapping.normalize("//") == '/'
    assert Mapping.normalize("//") == '/'
    assert Mapping.normalize('/test//') == '/test/'


def test_mapping_instanciation():
    with pytest.raises(ValueError) as exc:
        Mapping(test=1)
    assert str(exc.value) == "Path must start with '/', got 'test'"

    node = Mapping({"/test": basic_app})
    assert node == {'/test': basic_app}

    node = Mapping({"/": basic_app})
    assert node == {'/': basic_app}

    node = Mapping({"////": basic_app})
    assert node == {'/': basic_app}


def test_mapping_update():
    node = Mapping({"/test": basic_app})
    with pytest.raises(ValueError):
        node.update({1: basic_app})

    node.update({'/test': other_app})
    assert node['/test'] is other_app


def test_mapping_set_default():
    node = Mapping()
    node.setdefault('/test', basic_app)
    assert node['/test'] is basic_app


def test_mapping_items():
    node = Mapping({"/test": basic_app, '/other': other_app})
    assert list(node.items()) == [
        ('/test', basic_app),
        ('/other', other_app)
    ]


def test_mapping_repr():
    node = Mapping({"/test": basic_app, '/other': other_app})
    assert repr(node) == (
        f"{{'/test': {basic_app}, '/other': {other_app}}}"
    )


def test_mapping_set_del_item():
    node = Mapping()
    node['/'] = basic_app
    assert node == {'/': basic_app}

    with pytest.raises(ValueError) as exc:
        node['test'] = basic_app
    assert str(exc.value) == "Path must start with '/', got 'test'"

    del node['/']
    assert node == {}

    node['/'] = 1
    node['/'] = basic_app
    assert node == {'/': basic_app}

    script = node.pop('/')
    assert script is basic_app
    assert node == {}


def test_mapping_resolve():
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}
    node = Mapping({"/test": basic_app})
    assert node.resolve('/no', environ) is None
    assert environ == {'PATH_INFO': '/no', 'SCRIPT_NAME': ''}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/test'}
    node = Mapping({"/test": basic_app})
    assert node.resolve('/test', environ) is basic_app
    assert environ == {'PATH_INFO': '', 'SCRIPT_NAME': '/test'}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/'}
    node = Mapping({"/": basic_app})
    assert node.resolve('/', environ) is basic_app
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': ''}


def test_mapping_competing_apps():
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/backend'}
    node = Mapping({"/": basic_app, "/backend": other_app})
    assert node.resolve('/backend', environ) is other_app
    assert environ == {'PATH_INFO': '', 'SCRIPT_NAME': '/backend'}


def test_nested_mapping():
    from unittest.mock import Mock

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    response = node(environ, Mock())
    assert isinstance(response, Response)
    assert response.status == 404
    assert environ == {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/some'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    response = node(environ, Mock())
    assert response.status == 404
    assert environ == {'SCRIPT_NAME': '/some', 'PATH_INFO': ''}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/some/thing'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    response = node(environ, Mock())
    assert response == [b'Hello World!\n']
    assert environ == {'PATH_INFO': '', 'SCRIPT_NAME': '/some/thing'}
