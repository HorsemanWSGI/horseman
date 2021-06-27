import pytest
import logging
from webtest import TestApp as WSGIApp
from horseman.response import Response
from horseman.meta import Node, SentryNode
from horseman.http import HTTPError


class TestNode:

    def test_direct_instance(self):
        with pytest.raises(TypeError) as exc:
            Node()
        assert str(exc.value) == (
            "Can't instantiate abstract class Node "
            "with abstract methods resolve"
        )

    def test_call(self):

        class MyNode(Node):

            def resolve(self, path_info, environ):
                if path_info == "/test":
                    return Response.create(200, body=b"Some Content")

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


class TestSentryNode:

    def test_direct_instance(self):
        with pytest.raises(TypeError) as exc:
            SentryNode()
        assert str(exc.value) == (
            "Can't instantiate abstract class SentryNode "
            "with abstract methods handle_exception, resolve"
        )

    def test_call(self, caplog):
        import traceback

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
