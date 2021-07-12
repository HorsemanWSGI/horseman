horseman
********

WSGI Headless API helper


Example
=======

.. code-block::

  import logging
  from bjoern import run
  from horseman.meta import SentryNode, Overhead, APIView
  from horseman.response import Response


  class Request(Overhead):

      data = None

      def __init__(self, environ):
          self.environ = environ

      def extract(self):
          self.data = 'somedata'


  class View(APIView):

      def GET(self, overhead):
          return Response.to_json(200, {"Result": "OK"})


  VIEWS = {
      "/": View()
  }


  class RootNode(SentryNode):

      def resolve(self, path_info, environ):
          if view := VIEWS.get(path_info):
              request = Request(environ)
              return view(request)

      def handle_exception(self, exc_info, environ):
          logging.error(exc_info)


  run(
      host="0.0.0.0",
      port=8080,
      reuse_port=True,
      wsgi_app=RootNode(),
  )
