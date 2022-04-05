import pytest
import logging
from unittest.mock import Mock
from webtest import TestApp as WSGIApp
from horseman.response import Response
from horseman.meta import Node, SentryNode
from horseman.http import HTTPError


class TestNode:

    def test_direct_instance(self):
        # Can't instanciate directly a class with abstract methods.
        with pytest.raises(TypeError):
            Node()

    def test_call(self):

        class MyNode(Node):

            def resolve(self, path_info, environ):
                if path_info == "/test":
                    return Response(body=b"Some Content")

        node = WSGIApp(MyNode())
        response = node.get("/", expect_errors=True)
        assert response.status == "404 Not Found"

        response = node.get("/test", expect_errors=True)
        assert response.status == "200 OK"
        assert response.body == b"Some Content"

    def test_error_handling(self):

        class MyNode(Node):

            def resolve(self, path_info, environ):
                raise HTTPError(400, 'This is a dead end')

        node = WSGIApp(MyNode())
        response = node.get("/", expect_errors=True)
        assert response.status == "400 Bad Request"
        assert response.body == b'This is a dead end'

    def test_path_normalization(self):

        class MyNode(Node):

            def resolve(self, path_info, environ):
                return Response(body=path_info)

        node = WSGIApp(MyNode())
        assert node.get("/test").body == b'/test'
        assert node.get("///test//").body == b'/test/'
        assert node.get("///foo//bar////").body == b'/foo/bar/'
        assert node.get("").body == b''


class TestSentryNode:

    def test_direct_instance(self):
        with pytest.raises(TypeError) as exc:
            SentryNode()
        assert str(exc.value) == (
            "Can't instantiate abstract class SentryNode "
            "with abstract methods handle_exception, resolve"
        )

    def test_call(self, caplog):

        class MyNode(SentryNode):

            def handle_exception(self, exc_info, environ):
                logging.warning('An error occured !')

            def resolve(self, path_info, environ):
                raise NotImplementedError('I failed !')

        node = WSGIApp(MyNode())
        with caplog.at_level(logging.WARNING):
            with pytest.raises(NotImplementedError):
                node.get("/", expect_errors=True)

        assert len(caplog.records) == 1
        assert caplog.records[0].message == 'An error occured !'

    def test_close(self, caplog):

        class Response:

            def __iter__(self):
                yield b'I am done'

            def close(self):
                logging.info('I closed')

            def __call__(self, environ, start_response):
                start_response('200 OK', [])
                return self

        class MyNode(SentryNode):

            def handle_exception(self, exc_info, environ):
                pass

            def resolve(self, path_info, environ):
                return Response()

        node = WSGIApp(MyNode())
        with caplog.at_level(logging.INFO):
            node.get("/")

        assert len(caplog.records) == 1
        assert caplog.records[0].message == 'I closed'

    def test_close_exception(self, caplog):

        error = NotImplementedError("I don't know what to do !")

        class Response:

            def __iter__(self):
                yield b'I am done'

            def close(self):
                raise error

            def __call__(self, environ, start_response):
                start_response('200 OK', [])
                return self

        handle = Mock()

        class MyNode(SentryNode):

            def handle_exception(self, exc_info, environ):
                cls, exc, tb = exc_info
                handle(exc)

            def resolve(self, path_info, environ):
                return Response()

        node = WSGIApp(MyNode())
        with pytest.raises(NotImplementedError):
            node.get("/")

        assert handle.call_count == 1
        handle.assert_called_once_with(error)
