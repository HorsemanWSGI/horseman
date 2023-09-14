import pytest
import webtest
from horseman.mapping import Mapping
from horseman.response import Response
from horseman.exceptions import HTTPError


def basic_app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


def other_app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    return [b"Something else\n"]


def third_app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    return [b"Something else entirely\n"]


def test_mapping_instanciation():
    node = Mapping(test=basic_app)
    assert node == {'/test': basic_app}

    node = Mapping({"/test": basic_app})
    assert node == {'/test': basic_app}

    node = Mapping({"/": basic_app})
    assert node == {'/': basic_app}

    node = Mapping({"////": basic_app})
    assert node == {'/': basic_app}


def test_mapping_update():
    node = Mapping({"/test": basic_app})
    with pytest.raises(TypeError):
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

    node['test'] = basic_app
    assert node == {
        '/': basic_app,
        '/test': basic_app
    }

    del node['/']
    assert node == {'/test': basic_app}

    node['/'] = basic_app
    assert node == {'/': basic_app, '/test': basic_app}

    script = node.pop('/')
    assert script is basic_app
    assert node == {'/test': basic_app}


def test_mapping_resolve():
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}
    node = Mapping({"/test": basic_app})
    with pytest.raises(HTTPError) as exc:
        node.resolve('/no', environ)
    assert exc.value.status == 404

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/test'}
    node = Mapping({"/test": basic_app})
    assert node.resolve('/test', environ) is basic_app
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': '/test'}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/'}
    node = Mapping({"/": basic_app})
    assert node.resolve('/', environ) is basic_app
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': ''}


def test_mapping_competing_apps():
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/backend'}
    node = Mapping({"/": basic_app, "/backend": other_app})
    assert node.resolve('/backend', environ) is other_app
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': '/backend'}


def test_mapping_incomplete_name():
    node = Mapping({
        "/": basic_app,
        "/backend_app": other_app,
        "/backend_api/test": other_app,
        "/backend": third_app
    })
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/back'}
    assert node.resolve('/back', environ) is basic_app
    assert environ == {'PATH_INFO': '/back', 'SCRIPT_NAME': ''}

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/backend_app'}
    assert node.resolve('/backend_app', environ) is other_app
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': '/backend_app'}


def test_mapping_name_overspill():
    node = Mapping({
        "/": basic_app,
        "/backend": other_app
    })
    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/backender'}
    assert node.resolve('/backender', environ) is basic_app
    assert environ == {'PATH_INFO': '/backender', 'SCRIPT_NAME': ''}


def test_nested_mapping():
    from unittest.mock import Mock

    start_response = Mock()

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    body = b"".join(node(environ, start_response))
    start_response.assert_called_with('404 Not Found', [])
    assert environ == {'SCRIPT_NAME': '', 'PATH_INFO': '/no'}
    start_response.reset()

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/some'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    response = node(environ, start_response)
    start_response.assert_called_with('404 Not Found', [])
    assert environ == {'SCRIPT_NAME': '', 'PATH_INFO': '/some'}
    start_response.reset()

    environ = {'SCRIPT_NAME': '', 'PATH_INFO': '/some/thing'}
    node = Mapping({"/some":  Mapping({'/thing': basic_app})})
    response = node(environ, start_response)
    assert list(response) == [b'Hello World!\n']
    assert environ == {'PATH_INFO': '/', 'SCRIPT_NAME': '/some/thing'}
